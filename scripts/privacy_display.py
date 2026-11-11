"""Privacy-only display transforms; original scores and evidence stay immutable."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re

REVISION = 'privacy-v16-public70-display.1'
ROOT = Path(__file__).resolve().parents[1]


def update_file_hashes(index, root, outputs):
    records = {record['path']: record for record in index['records']}
    for output, content in outputs.items():
        name = output.relative_to(root).as_posix()
        if name not in records:
            records[name] = {'path': name}
            index['records'].append(records[name])
        records[name]['public_display_sha256'] = sha256(content).hexdigest()


@lru_cache(maxsize=1)
def rules():
    path = ROOT / 'config/privacy.local.json'
    return json.loads(path.read_text()) if path.is_file() else {}


def infer_task(path):
    selected = ROOT / 'config/selections/current.json'
    if not selected.is_file():
        return None
    ids = set(json.loads(selected.read_text())['task_ids'])
    return next((part for part in reversed(Path(path).parts) if part in ids), None)


def scrub(text, task_id=None):
    policy = rules()
    replacements = dict(policy.get('common', {}))
    case = policy.get('tasks', {}).get(task_id, {})
    replacements.update(case.get('literals', {}))
    for old, new in sorted(replacements.items(), key=lambda x: -len(x[0])):
        text = text.replace(old, new)
    for old, new in sorted(case.get('rankings', {}).items(), key=lambda x: -len(x[0])):
        def rank_variant(match):
            before = text[max(0, match.start()-30):match.start()]
            if old.endswith('%') and re.search(r'(?:保研率|推免率|名额比例|就业率|升学率|就业升学率|直博生占比)[^，。；\n]{0,24}$', before):
                return match.group()
            return new
        text = re.sub(r'(?<![\d.])' + re.escape(old) + r'(?!\d)', rank_variant, text)
    # An exact student score may appear without a CET label in a profile table.
    # Preserve comparisons, admission thresholds, score decimals, IDs and hashes.
    for old, new in case.get('language_scores', {}).items():
        pattern = r'(?<![A-Za-z0-9._/≥≤<>-])' + old + r'(?![A-Za-z0-9._/–—-])'
        def replace(match):
            before = text[max(0, match.start()-55):match.start()]
            after = text[match.end():match.end()+35]
            # Personal scores sometimes appear below a heading about thresholds.
            personal = re.search(r'(?:现有|已有|你的|你目前|你已|你是谁|针对|对照|申请人|专业第|排名)[^，。；\n|]{0,35}$', before) or re.match(r'[\s*]*(?:分[\s*]*)?(?:在|过|对多数|是你|对照|是否达标|远超|均达标|通常|说明|最适合|可作为|的短板|[<>]\s*\d{3})', after)
            if personal:
                return new
            if re.search(r'(?:至少|要求|门槛|申请资格|申请条件|入营条件|硬线|明线|不低于|高于|低于|达到)[^，。；\n|]{0,40}$', before) or re.search(r'[≥≤<>]\s*$', before):
                return match.group()
            return new
        text = re.sub(pattern, replace, text)
    # School names used as destination recommendations remain intact.
    for old, new in case.get('undergraduate_schools', {}).items():
        pattern = r'((?:本科(?:院校|学校)?|就读学校|毕业学校|学生来自|你来自|您来自|你在|您在|我在|本科学校为)[：:是为\s]*)' + re.escape(old)
        text = re.sub(pattern, lambda m: m[1] + new, text)
        pattern = r'(?m)(\|\s*(?:本科院校|本科学校|就读院校|学校)\s*\|\s*)' + re.escape(old)
        text = re.sub(pattern, lambda m: m[1] + new, text)
    # Only personal profile clauses are affected; official target names stay intact.
    for old, new in case.get('undergraduate_schools', {}).items():
        pattern = r'(?m)^.*' + re.escape(old) + r'.*$'
        def profile(match):
            line = match.group()
            if re.search(r'本科|学生背景|个人背景|背景画像|你的背景|您的背景|基本背景|你的情况|您的情况|学校背景', line):
                if not re.search(r'推荐项目|参考项目|候选项目|目标院校|申请目标', line):
                    return line.replace(old, new)
            return line
        text = re.sub(pattern, profile, text)
    text = re.sub(r'排名前(?:约)?前约', '排名前约', text)
    text = re.sub(r'(?<=排名)\d{1,2}\.\d+%', lambda m: f'前约{round(float(m[0][:-1]))}%', text)
    text = re.sub(r'((?:你|申请人)[^，。；\n]{0,12}(?:前|排名前?))([0-9]{1,2}\.[0-9]+)%', lambda m: m[1] + f'约{round(float(m[2]))}%', text)
    text = re.sub(r'(?:你|申请人)[^，。；\n]{0,12}\d{1,2}\.\d+%', lambda m: re.sub(r'\d{1,2}\.\d+%', lambda n: f'约{round(float(n[0][:-1]))}%', m[0]), text)
    text = re.sub(r'GPA[：:\s]*(?:\d(?:\.\d+)?\s*/\s*\d(?:\.\d+)?|\d\.\d+)', '课程成绩已概括', text)
    text = re.sub(r'(?:递补|资格队列)[（(]?(?:第)?11(?:位|名)?[）)]?', '资格确认', text)
    def personal_language(match):
        before = text[max(0, match.start()-30):match.start()]
        after = text[match.end():match.end()+30]
        if re.search(r'要求|门槛|至少|不低于|专业不限', before):
            return match.group()
        if re.search(r'你是谁|短板|互相印证|竞赛|佐证', before+after) or after.startswith('——'):
            n = int(match[2]); low = 425 if 425 <= n < 450 else n//50*50
            return match[1] + f'{low}–{449 if low==425 else low+49}'
        return match.group()
    text = re.sub(r'((?:四级|六级)\s*[:：]?\s*)(\d{3})(?![\d–-])', personal_language, text)
    text = text.replace('约约', '约').replace('专业第前约', '专业排名前约').replace('前 前约', '前约').replace('前前约', '前约')
    return text


def scrub_value(value, task_id=None):
    if isinstance(value, dict):
        task_id = value.get('task_id', value.get('source_task_id', task_id))
        immutable = {'model', 'cli', 'cli_version', 'agent', 'adapter', 'adapter_version', 'auth_mode', 'started_at', 'finished_at', 'generated_at', 'updated_at', 'status', 'execution_status', 'review_status', 'score_status', 'scoring_status'}
        return {k: v if k in immutable or k.endswith('sha256') else scrub_value(v, task_id) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub_value(v, task_id) for v in value]
    return scrub(value, task_id) if isinstance(value, str) else value
