#!/usr/bin/env python3
"""Render the single selected model/task answer index from public records."""
from collections import defaultdict
from pathlib import Path
import json

if __package__:
 from .privacy_display import update_file_hashes
else:
 from privacy_display import update_file_hashes

ROOT = Path(__file__).resolve().parents[1]
ANSWERS = ROOT / 'experiments/records70'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def interval(v):return f'{v[0]:.2f}' if v[0]==v[1] else f'{v[0]:.2f}–{v[1]:.2f}'
def render():
 rows=read(ANSWERS/'score-details-70.json')['rows']
 ranking=read(ANSWERS/'score-summary-70.json')['ranking']
 outputs={}
 grouped=defaultdict(list)
 for row in rows:grouped[row['agent']].append(row)
 for agent,own in grouped.items():
  model=own[0]['name'];root=ANSWERS/'models'/agent
  lines=[f'# {model} · 70题逐题结果 / Per-task results','',
         '[所有模型 / All models](../../README.md) · [计分方法 / Methodology](../../../../docs/result-methodology.md)','',
         '| 题号 / Task | 分数 / Score | 答卷 / Answer | 评审 / Review | 执行信息 / Execution |',
         '| --- | ---: | --- | --- | --- |']
  for row in sorted(own,key=lambda x:x['question_id']):
   task=row['task_id'];folder=root/task
   assert folder.is_dir()
   answer=row.get('answer_path')
   if answer:
    p=ANSWERS/answer;assert p.is_file()
    alink=f'[答卷 / Answer]({task}/{p.relative_to(folder).as_posix()})'
   else:alink='原始正文未留存 / Original text unavailable'
   review=[]
   for name,label in [('judgment.json','逐项评审 / Judgment'),('score.json','评分 / Score'),('effective-score.json','生效分 / Effective score'),('adjudication.json','裁定 / Ruling'),('node-adjudication.json','节点裁定 / Node ruling')]:
    if (folder/name).is_file():review.append(f'[{label}]({task}/{name})')
   meta=[]
   for name,label in [('metadata.json','元数据 / Metadata'),('run.json','运行 / Execution')]:
    if (folder/name).is_file():meta.append(f'[{label}]({task}/{name})')
   lines.append(f"| {row['question_id']} · {task} | {interval(row['interval'])} | {alink} | {' · '.join(review) or '—'} | {' · '.join(meta) or '—'} |")
  lines+=['','分数区间表示仍有待核事实；任务目录保存该题当前选定记录。','Score ranges retain unresolved facts; each task directory holds the current selected record.','']
  if (root/'manifest.json').is_file():lines+=['[运行与评分记录 / Run and scoring record](manifest.json)', '']
  outputs[root/'README.md']='\n'.join(lines).encode('utf-8')
 lines=['# 按模型查阅答卷与评分 / Answers and scores by model','',
        '本页按模型整理当前70题的答卷、评分及运行记录；均分仅展示已有评分的配置。各模型目录下按题号保存答卷、评审、评分与执行元数据；正文不可用的题目仍显示已有分数和状态。','',
        'This page organizes answers, scores and execution records for the current 70 tasks by model; means are shown only for scored configurations. Each model has one folder per task with available answer, review, score and execution metadata; scores and statuses remain visible where answer text is unavailable.','',
        '| 模型 / Model | 70题均分 / Mean | 完成 / Completed | 逐题记录 / Tasks |','| --- | ---: | ---: | --- |']
 agents={x['name']:x['agent'] for x in rows}
 for model in ranking:
  agent=agents[model['model']];lines.append(f"| {model['model']} | {interval(model['mean_score_interval'])} | {model['completed_count']}/70 | [查看 / Open](models/{agent}/README.md) |")
 # Keep unscored run records discoverable without adding them to ranking data.
 for manifest in sorted((ANSWERS/'models').glob('*/manifest.json')):
  record=read(manifest)
  if record.get('scored') is not False or record.get('leaderboard_included') is not False:continue
  config=record['agent_configuration'];agent=manifest.parent.name
  if agent in grouped:continue
  model=f"{config['system']} + {config['model']}"
  lines.append(f"| {model}（未评分 / Unscored） | — | {record['counts']['completed']}/{record['planned_tasks']} | [查看 / Open](models/{agent}/README.md) |")
 lines+=['','[主榜数据 / Ranking](score-summary-70.json) · [逐题数据 / Per-task data](score-details-70.json)','']
 outputs[ANSWERS/'README.md']='\n'.join(lines).encode('utf-8')
 index_path=ANSWERS/'privacy-display.json'
 if index_path.is_file():
  index=read(index_path)
  update_file_hashes(index, ROOT, outputs)
  outputs[index_path]=(json.dumps(index,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 for path, content in outputs.items():
  path.write_bytes(content)
if __name__=='__main__':render()
