#!/usr/bin/env python3
"""Render score charts from public ranking data (optional Matplotlib tooling).

Only the four score charts are generated. Use render_current70_figures.py
to refresh the leaderboard and its figures together.

The original PDF figures use Liberation Sans and Noto Sans CJK SC. When these
fonts are not installed, pass a directory containing the font files.
"""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findfont, fontManager
from matplotlib.ticker import MultipleLocator

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/figures/dev70-current'
DATA = ROOT / 'experiments/records70/score-summary-70.json'
LABELS = {
    'GPT Sol': ('Codex', 'GPT Sol 6.1', '#f09a9b'),
    'GPT Astra': ('Codex', 'GPT Astra 6', '#fbdddd'),
    'DeepSeek V4.1 Flash': ('DSH', 'DeepSeek V4.1 Flash', '#90b7e2'),
    'GLM 5.3 Flash': ('Volcengine Managed Agent', 'GLM 5.3 Flash', '#aac8ea'),
    'Qwen3.8 Max': ('Qwen Code', 'Qwen3.8 Max', '#c4d9f1'),
    'WorkBuddy + Hy4 preview': ('WorkBuddy', 'Hy4 preview', '#65ad9f'),
    'Kimi K3': ('Kimi Code', 'Kimi K3', '#dce8f7'),
    'Gemini 3.8 Flash': ('Antigravity', 'Gemini 3.8 Flash', '#8086c0'),
    'Gemini 3.1 Pro': ('Antigravity', 'Gemini 3.1 Pro', '#bbb9ed'),
}
CATEGORIES = ('recommendation_single', 'planning_single', 'staged')
WIDTH = 2048
OVERALL_WIDTH_PT = 496.875
CATEGORY_WIDTH_PT = 554.3606


def figure_size(width_pt, height_px):
    width_in = width_pt / 72
    return width_in, width_in * height_px / WIDTH


def chart_label(name):
    if name in LABELS:
        return LABELS[name]
    system, _, model = name.partition(' + ')
    return system, model, '#8fa6b5'


def render(font_dir=None, *, data=None, output_dir=OUT):
    if data is None:
        data = json.loads(DATA.read_text())
    ranking = data['ranking']
    count = len(ranking)
    if not count:
        raise ValueError('No agent configurations to plot')
    questions = data['question_count']
    labels = [chart_label(row['model']) for row in ranking]
    en_configurations = f'{count} agent configuration' + ('s' if count != 1 else '')
    if font_dir is not None:
        for path in sorted(font_dir.iterdir()):
            if path.suffix.lower() in {'.ttf', '.otf'}:
                fontManager.addfont(path)
    latin = 'Liberation Sans'
    chinese = 'Noto Sans CJK SC'
    for family in (latin, chinese):
        findfont(FontProperties(family=[family]), fallback_to_default=False)
    font = FontProperties(family=[latin])
    cjk = FontProperties(family=[latin, chinese])
    plt.rcParams.update({'font.family': latin, 'axes.linewidth': 1,
                         'mathtext.fontset': 'custom', 'mathtext.it': f'{latin}:italic',
                         'mathtext.rm': latin, 'savefig.facecolor': 'white'})
    colors = [color for _, _, color in labels]

    def axis(ax, values, label_sizes, tick_step):
        ax.barh(range(count), values, height=.66, color=colors,
                edgecolor='#1a1a1a', linewidth=.8)
        ax.set(xlim=(0, 100), ylim=(count-.4, -.6), yticks=[],
               xticks=range(0, 101, tick_step))
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
        ax.tick_params(axis='x', width=1, length=4, labelsize=10, pad=3.5)
        if label_sizes is not None:
            agent_size, model_size = label_sizes
            label_x = -.045 if tick_step == 25 else -.018
            for i, (top, bottom, _) in enumerate(labels):
                ax.text(label_x, i-.20 if bottom else i, top, transform=ax.get_yaxis_transform(),
                        ha='right', va='center', fontsize=agent_size, fontproperties=cjk, clip_on=False)
                if bottom:
                    ax.text(label_x, i+.16, bottom, transform=ax.get_yaxis_transform(),
                            ha='right', va='center', fontsize=model_size, fontproperties=cjk,
                            color='#666', clip_on=False)

    for lang in ('en', 'zh'):
        zh = lang == 'zh'
        fp = cjk if zh else font
        score_label = '平均得分（0–100）' if zh else 'Mean score (0–100)'
        note = (f'注：基于公开 {questions} 题的选定记录。各配置使用原版题目作答，公开脱敏文本用于展示。运行设置见评测说明。'
                if zh else f'Note: Based on selected records for {questions} public tasks. Agents answered the original task inputs.\n'
                'Public text is de-identified for display. See the project documentation for run settings.')
        height = (1654 if zh else 1687) + (count - 9) * 142
        fig, ax = plt.subplots(figsize=figure_size(OVERALL_WIDTH_PT, height))
        fig.subplots_adjust(left=.284, right=.969, top=1-26/height,
                            bottom=(347 if zh else 374)/height)
        means = [r['mean_score_interval'][0] for r in ranking]
        axis(ax, means, label_sizes=(10.5, 9.3), tick_step=20)
        ax.xaxis.set_minor_locator(MultipleLocator(10))
        ax.tick_params(axis='x', which='minor', width=.75, length=2.5)
        for i, value in enumerate(means):
            ax.text(value+.8, i, f'{value:.2f}', va='center', fontsize=9.5)
        ax.set_xlabel(score_label, fontproperties=fp, fontsize=11.5, labelpad=5)
        caption = (f'{count} 组 Agent 配置在 {questions} 项评测任务上的平均得分（满分 100）' if zh
                   else f'Mean scores of {en_configurations} across {questions} evaluation tasks (maximum = 100)')
        fig.text(.5, (121 if zh else 157)/height, caption, ha='center', va='center',
                 fontproperties=fp, fontsize=10.5 if zh else 10)
        fig.text(.5, (50 if zh else 65)/height, note, ha='center', va='center',
                 fontproperties=fp, fontsize=8.5 if zh else 7.8, color='#444')
        fig.savefig(output_dir/f'fig1_{lang}_workbuddy.png', dpi=WIDTH / fig.get_figwidth())
        plt.close(fig)

        height = (1376 if zh else 1404) + (count - 9) * 102
        fig, axes = plt.subplots(1, 3, figsize=figure_size(CATEGORY_WIDTH_PT, height))
        fig.subplots_adjust(left=.232, right=.957, top=1-(132 if zh else 117)/height,
                            bottom=(326 if zh else 356)/height, wspace=.265)
        names = (('择校推荐', '规划与决策', '两阶段任务') if zh
                 else ('School Recommendation', 'Planning and Decision-Making', 'Two-Stage Tasks'))
        for col, category in enumerate(CATEGORIES):
            ax = axes[col]
            values = [r['categories'][category]['mean_score_interval'][0] for r in ranking]
            axis(ax, values, label_sizes=(9.5, 8.4) if col == 0 else None, tick_step=25)
            if col:
                ax.spines['left'].set_visible(False)
            highest = max(values)
            for i, value in enumerate(values):
                ax.text(value+1.1, i, f'{value:.2f}', va='center', fontsize=8,
                        fontweight='bold' if value==highest else 'normal')
            category_count = data['category_counts'][category]
            count_label = f'（N = {category_count}）' if zh else f'($N$ = {category_count})'
            ax.set_title(f'({chr(97+col)}) {names[col]}\n{count_label}',
                         fontproperties=fp, fontsize=10.5 if zh else 9, pad=4)
        fig.supxlabel(score_label, x=.605, y=(190 if zh else 216)/height,
                      fontproperties=fp, fontsize=10.5)
        caption = (f'{count} 组 Agent 配置在三类任务上的平均得分对比（各类最高分以粗体标出）' if zh
                   else f'Mean scores of {en_configurations} by task category (highest score in each category in bold)')
        fig.text(.5, (109 if zh else 141)/height, caption, ha='center', va='center',
                 fontproperties=fp, fontsize=10.5 if zh else 10)
        fig.text(.5, (45 if zh else 60)/height, note, ha='center', va='center',
                 fontproperties=fp, fontsize=8.5 if zh else 7.8, color='#444')
        fig.savefig(output_dir/f'fig3_{lang}_workbuddy.png', dpi=WIDTH / fig.get_figwidth())
        plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font-dir', type=Path, help='Directory with the original fonts')
    render(parser.parse_args().font_dir)
