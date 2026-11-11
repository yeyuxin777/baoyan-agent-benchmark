#!/usr/bin/env python3
"""Refresh the current score charts and verify the supplied PNG figures.

Pass --source to import scores and refresh the leaderboard rows.
Pass --update-readmes to refresh the rows from the existing scores.
Rendering requires Matplotlib and the original fonts. Use --font-dir when
Liberation Sans and Noto Sans CJK SC are not installed.
"""
import argparse
from collections import Counter
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

if __package__:
    from .privacy_display import update_file_hashes
else:
    from privacy_display import update_file_hashes

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[1]
PUBLIC = ROOT / 'experiments/records70/score-summary-70.json'
FIGURES = ROOT / 'docs/figures/dev70-current'
CHART_RENDERER = ROOT / 'scripts/render_agent_score_charts.py'
CATEGORIES = ('recommendation_single', 'planning_single', 'staged')
SCORE_FIGURES = (
    'fig1_en_workbuddy.png', 'fig1_zh_workbuddy.png',
    'fig3_en_workbuddy.png', 'fig3_zh_workbuddy.png',
)
SUPPLIED_FIGURES = (
    'fig2_en.png', 'fig2_zh.png',
    'fig_diff_en.png', 'fig_diff_zh.png',
    'fig_task_en.png', 'fig_task_zh.png',
)
CONFIGURATION_LABELS = {
    'GPT Sol': 'Codex + GPT Sol 6.1',
    'GPT Astra': 'Codex + GPT Astra 6',
    'DeepSeek V4.1 Flash': 'DSH + DeepSeek V4.1 Flash',
    'GLM 5.3 Flash': 'Volcengine Managed Agent + GLM 5.3 Flash',
    'Qwen3.8 Max': 'Qwen Code + Qwen 3.8 Max',
    'WorkBuddy + Hy4 preview': 'WorkBuddy + Hy4 preview',
    'Kimi K3': 'Kimi Code + Kimi K3',
    'Gemini 3.8 Flash': 'Antigravity + Gemini 3.8 Flash',
    'Gemini 3.1 Pro': 'Antigravity + Gemini 3.1 Pro',
}


def read(path):
    return json.loads(path.read_text())


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


def fmt(bounds):
    return f'{bounds[0]:.2f}' if bounds[0] == bounds[1] else f'{bounds[0]:.2f}–{bounds[1]:.2f}'


def prepare_scores(source, selected, previous_rows):
    raw = read(source)
    tasks = {r['task_id']: r for r in selected['tasks']}
    counts = Counter(t['category'] for t in tasks.values())
    assert counts == Counter(dict(zip(CATEGORIES, (21, 36, 13))))
    assert raw['summary'] and len(raw['rows']) == 70 * len(raw['summary'])
    ranking = []
    for rank, model in enumerate(raw['summary'], 1):
        own = [r for r in raw['rows'] if r['agent'] == model['agent']]
        assert len(own) == 70 and {r['task_id'] for r in own} == set(tasks)
        assert all(r['question_id'] == tasks[r['task_id']]['question_id'] and r['category'] == tasks[r['task_id']]['category'] for r in own)
        categories = {}
        totals = [sum((Decimal(str(r['interval'][i])) for r in own), Decimal(0)) for i in (0, 1)]
        assert [float(v) for v in totals] == model['total_interval']
        assert [float(v/70) for v in totals] == model['mean_interval']
        for category in CATEGORIES:
            group = [r for r in own if r['category'] == category]
            sums = [sum((Decimal(str(r['interval'][i])) for r in group), Decimal(0)) for i in (0, 1)]
            categories[category] = {'question_count': len(group),
                                    'total_score_interval': [float(v) for v in sums],
                                    'mean_score_interval': [float(v/len(group)) for v in sums]}
        ranking.append({'rank': rank, 'model': model['name'], 'question_count': 70,
                        'total_score_interval': [float(v) for v in totals],
                        'mean_score_interval': [float(v/70) for v in totals], 'categories': categories,
                        **{k: model[k] for k in ('completed_count', 'timeout_count', 'completion_rate', 'pending_answer_count') if k in model}})
    exported = {'question_count': 70, 'points_per_question': 100, 'maximum_total_score': 7000,
                'generated_at': raw['generated_at'], 'official': False,
                'category_counts': dict(counts), 'ranking': ranking}
    if raw.get('score_note'):
        exported['score_note'] = raw['score_note']
    fields = ('agent', 'name', 'task_id', 'question_id', 'category', 'interval', 'pending_nodes',
              'answer_status', 'source_kind', 'answer_sha256')
    previous_by_task = {(row['agent'], row['task_id']): row for row in previous_rows}
    rows = []
    for raw_row in raw['rows']:
        previous = previous_by_task.get((raw_row['agent'], raw_row['task_id']), {})
        answer_hash = raw_row.get('answer_sha256')
        # Keep reviewed public metadata only when the import refers to the same answer.
        row = previous.copy() if answer_hash and previous.get('answer_sha256') == answer_hash else {}
        row.update({key: raw_row[key] for key in fields if key in raw_row})
        rows.append(row)
    exported['selected_record_count'] = len(rows)
    exported['answer_text_available_count'] = sum(bool(row.get('answer_path')) for row in rows)
    details = {
        'official': False, 'question_count': 70, 'generated_at': raw['generated_at'],
        'score_note': raw.get('score_note', {}),
        'rows': rows}
    return exported, details


def check_scores(data, selected):
    assert data['question_count'] == selected['task_count'] == 70
    assert data['category_counts'] == selected['counts']
    assert data['ranking']
    assert len({r['model'] for r in data['ranking']}) == len(data['ranking'])
    for r in data['ranking']:
        assert r['question_count'] == 70
        if 'completed_count' in r:
            assert r['completed_count'] + r['timeout_count'] == 70
            assert r['completion_rate'] == r['completed_count'] / 70
        for category in CATEGORIES:
            c = r['categories'][category]
            assert c['question_count'] == data['category_counts'][category]
            assert 0 <= c['mean_score_interval'][0] <= c['mean_score_interval'][1] <= 100
        for i in (0, 1):
            total = sum(Decimal(str(r['categories'][c]['total_score_interval'][i])) for c in CATEGORIES)
            assert abs(total-Decimal(str(r['total_score_interval'][i]))) < Decimal('0.000000001')
            assert abs(total/70-Decimal(str(r['mean_score_interval'][i]))) < Decimal('0.000000001')


def check_details(data, details, selected):
    tasks = {r['task_id']: r for r in selected['tasks']}
    assert len(details['rows']) == 70 * len(data['ranking'])
    for model in data['ranking']:
        own = [r for r in details['rows'] if r['name'] == model['model']]
        assert len(own) == 70 and {r['task_id'] for r in own} == set(tasks)
        for r in own:
            assert r['question_id'] == tasks[r['task_id']]['question_id']
            assert r['category'] == tasks[r['task_id']]['category']
            assert 0 <= r['interval'][0] <= r['interval'][1] <= 100
            if r.get('answer_status') == 'timeout':
                assert r['interval'] == [0, 0]
        if 'completed_count' in model:
            assert sum(r['answer_status'] == 'completed' for r in own) == model['completed_count']
            assert sum(r['answer_status'] == 'timeout' for r in own) == model['timeout_count']
        for i in (0, 1):
            total = sum((Decimal(str(r['interval'][i])) for r in own), Decimal(0))
            assert abs(total - Decimal(str(model['total_score_interval'][i]))) < Decimal('0.000000001')


def readme_results(data, details, zh):
    path = ROOT/('README.zh-CN.md' if zh else 'README.md')
    original = path.read_text()
    heading = '## 评测结果' if zh else '## Evaluation results'
    next_heading = '## 快速开始' if zh else '## Quick start'
    section_start, section_end = original.index(heading), original.index(next_heading)
    table_start = original.index('| ', section_start)
    rows_start = original.index('\n', original.index('\n', table_start) + 1) + 1
    rows_end = original.index('\n\n', rows_start)
    assert rows_end < section_end
    model_agents = {r['name']: r['agent'] for r in details['rows']}
    lines = []
    for r in data['ranking']:
        completed = f"{r['completed_count']}/70 ({r['completion_rate']:.1%})" if 'completed_count' in r else '—'
        label = CONFIGURATION_LABELS.get(r['model'], r['model'])
        link = f"[{label}](experiments/records70/models/{model_agents[r['model']]}/README.md)"
        lines.append(f"| {r['rank']} | {link} | 70 | {completed} | {fmt(r['mean_score_interval'])} |")
    return path, (original[:rows_start]+'\n'.join(lines)+original[rows_end:]).encode('utf-8')


def png_bytes(path):
    content = path.read_bytes()
    if not content.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError(f'Invalid PNG figure: {path}')
    return content


def score_figures_current(manifest, source_hash, renderer_hash):
    if manifest.get('source_sha256') != source_hash:
        return False
    renderer_path = str(CHART_RENDERER.relative_to(ROOT))
    if manifest.get('source_files_sha256', {}).get(renderer_path) != renderer_hash:
        return False
    hashes = manifest.get('files', {})
    return all((FIGURES/name).is_file() and file_hash(FIGURES/name) == hashes.get(name)
               for name in SCORE_FIGURES)


def refresh_public_file_index(path, outputs, details):
    index = read(path)
    update_file_hashes(index, ROOT, outputs)
    rows = details['rows']
    available = sum(bool(row.get('answer_path')) for row in rows)
    index['selected_task_records'] = len(rows)
    index['answer_text_available_count'] = available
    index['answer_text_unavailable_count'] = len(rows) - available
    return json_bytes(index)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--update-readmes', action='store_true')
    parser.add_argument('--font-dir', type=Path)
    args = parser.parse_args()
    selection_path = ROOT/'config/selections/current.json'
    selected = read(selection_path)
    example_path = ROOT/'data/staged-dev/O03-04/task.json'
    rubric_path = example_path.with_name('rubric.json')
    details_path = PUBLIC.with_name('score-details-70.json')
    outputs = {}
    if args.source:
        previous_rows = read(details_path)['rows'] if details_path.is_file() else []
        data, details = prepare_scores(args.source, selected, previous_rows)
        summary_content = json_bytes(data)
        outputs[PUBLIC] = summary_content
        outputs[details_path] = json_bytes(details)
    else:
        summary_content = PUBLIC.read_bytes()
        data = json.loads(summary_content)
        details = read(details_path)
    check_scores(data, selected)
    check_details(data, details, selected)
    update_readmes = bool(args.source or args.update_readmes)
    if update_readmes:
        for zh in (False, True):
            path, content = readme_results(data, details, zh)
            outputs[path] = content

    manifest_path = FIGURES/'results-manifest.json'
    previous = read(manifest_path) if manifest_path.is_file() else {}
    source_hash = sha256(summary_content).hexdigest()
    renderer_hash = file_hash(CHART_RENDERER)
    files = {name: sha256(png_bytes(FIGURES/name)).hexdigest() for name in SUPPLIED_FIGURES}
    if score_figures_current(previous, source_hash, renderer_hash):
        score_charts = {FIGURES/name: png_bytes(FIGURES/name) for name in SCORE_FIGURES}
    else:
        try:
            if __package__:
                from .render_agent_score_charts import render
            else:
                from render_agent_score_charts import render
            with TemporaryDirectory(prefix='benchmark-score-charts-') as temp:
                render(args.font_dir, data=data, output_dir=Path(temp))
                score_charts = {FIGURES/name: png_bytes(Path(temp)/name) for name in SCORE_FIGURES}
            outputs.update(score_charts)
        except (ImportError, OSError, ValueError) as error:
            parser.error(f'Could not render score charts: {error}')
    files.update({path.name: sha256(content).hexdigest() for path, content in score_charts.items()})

    source_files = (PUBLIC, details_path, selection_path, example_path, rubric_path,
                    SCRIPT, CHART_RENDERER)
    source_hashes = {
        str(path.relative_to(ROOT)): (
            sha256(outputs[path]).hexdigest() if path in outputs else file_hash(path)
        ) for path in source_files if path in outputs or path.exists()
    }
    manifest = {'contains_model_scores': True, 'task_count': 70,
                'stage_count': 83, 'case_group_count': selected['case_group_count'],
                'model_count': len(data['ranking']), 'files': files,
                'source_sha256': source_hash, 'source_files_sha256': source_hashes,
                'generator': 'scripts/render_current70_figures.py'}
    outputs[manifest_path] = json_bytes(manifest)
    index_path = PUBLIC.with_name('privacy-display.json')
    if index_path.is_file():
        outputs[index_path] = refresh_public_file_index(index_path, outputs | score_charts, details)
    for path, content in outputs.items():
        path.write_bytes(content)
    print(json.dumps({'figures': len(files), 'models': len(data['ranking']),
                      'categories': data['category_counts'], 'readmes_updated': update_readmes}))


if __name__ == '__main__':
    main()
