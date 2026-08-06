#!/usr/bin/env python3
"""
MdMax Material Design v3 - Animated Graphics Generator
Creates stunning Material Design v3 dashboards with animations
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
import numpy as np
from pathlib import Path
import imageio
from PIL import Image, ImageDraw, ImageFont
import io

# Material Design v3 Colors
MD3_PRIMARY = '#6750a4'
MD3_SECONDARY = '#625b71'
MD3_TERTIARY = '#7d5260'
MD3_SUCCESS = '#2dd36f'
MD3_ERROR = '#f2231c'
MD3_WARNING = '#f9a825'
MD3_INFO = '#0d47a1'
MD3_BG = '#fffbfe'
MD3_SURFACE = '#fffbfe'

def create_animated_dashboard():
    """Create animated dashboard GIF with Material Design v3"""

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.patch.set_facecolor(MD3_BG)

    # Remove axis spines for clean look
    for ax in axes.flat:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#e0e0e0')
        ax.spines['bottom'].set_color('#e0e0e0')
        ax.set_facecolor(MD3_SURFACE)

    frames = []
    num_frames = 60

    for frame in range(num_frames):
        # Clear previous plots
        for ax in axes.flat:
            ax.clear()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#e0e0e0')
            ax.spines['bottom'].set_color('#e0e0e0')
            ax.set_facecolor(MD3_SURFACE)

        progress = frame / num_frames

        # ===== GRÁFICO 1: Economia por Formato =====
        ax1 = axes[0, 0]
        formats = ['PDF', 'Excel', 'Word', 'PowerPoint', 'EPUB', 'Images']
        target_savings = [80, 65, 50, 70, 82, 70]
        current_savings = [s * progress for s in target_savings]

        colors = [MD3_PRIMARY, MD3_SECONDARY, MD3_TERTIARY, MD3_SUCCESS, MD3_WARNING, MD3_INFO]
        bars = ax1.bar(formats, current_savings, color=colors, edgecolor='#333333', linewidth=1.5)
        ax1.set_ylabel('Token Savings (%)', fontsize=11, fontweight='bold', color='#333333')
        ax1.set_title('Economia por Formato', fontsize=12, fontweight='bold', pad=15, color='#333333')
        ax1.set_ylim(0, 100)
        ax1.axhline(y=79.7, color=MD3_ERROR, linestyle='--', linewidth=2, alpha=0.7)

        # Adicionar valores
        for bar, val in zip(bars, current_savings):
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
                        f'{int(height)}%', ha='center', va='bottom', fontweight='bold', fontsize=9)

        # ===== GRÁFICO 2: Comparação Antes/Depois =====
        ax2 = axes[0, 1]
        categories = ['31MB PDF', '6MB Excel', '50MB Doc']
        before = [31, 6, 50]
        after = [6.2, 1.2, 10]

        x = np.arange(len(categories))
        width = 0.35

        bars1 = ax2.bar(x - width/2, before, width, label='Original',
                       color=MD3_ERROR, edgecolor='#333333', linewidth=1.5, alpha=0.7)
        bars2 = ax2.bar(x + width/2, [a * progress for a in after], width, label='MdMax',
                       color=MD3_SUCCESS, edgecolor='#333333', linewidth=1.5)

        ax2.set_ylabel('Tamanho (MB)', fontsize=11, fontweight='bold', color='#333333')
        ax2.set_title('Antes vs Depois', fontsize=12, fontweight='bold', pad=15, color='#333333')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories, fontsize=9)
        ax2.legend(loc='upper right')
        ax2.set_ylim(0, 55)

        # ===== GRÁFICO 3: Economia de Tokens =====
        ax3 = axes[0, 2]
        scenarios = ['1 PDF', '10 Files', '100 Files', '1000 Files']
        tokens_saved = [2850, 28500, 285000, 928800]
        current_tokens = [t * progress for t in tokens_saved]

        bars = ax3.bar(scenarios, current_tokens, color=MD3_PRIMARY,
                      edgecolor='#333333', linewidth=1.5)
        ax3.set_ylabel('Tokens Economizados', fontsize=11, fontweight='bold', color='#333333')
        ax3.set_title('Economia de Tokens', fontsize=12, fontweight='bold', pad=15, color='#333333')

        # ===== GRÁFICO 4: Performance =====
        ax4 = axes[1, 0]
        formats_perf = ['PDF', 'XLSX', 'CSV', 'JSON', 'DOCX']
        processing_time = [3.2, 1.5, 0.8, 0.5, 1.2]
        current_time = [t * progress for t in processing_time]

        bars = ax4.barh(formats_perf, current_time, color=MD3_TERTIARY,
                       edgecolor='#333333', linewidth=1.5)
        ax4.set_xlabel('Tempo (segundos)', fontsize=11, fontweight='bold', color='#333333')
        ax4.set_title('Performance por Formato', fontsize=12, fontweight='bold', pad=15, color='#333333')
        ax4.set_xlim(0, 3.5)

        # ===== GRÁFICO 5: ROI =====
        ax5 = axes[1, 1]
        months = np.arange(1, 13)
        cumulative_savings = np.array([77, 154, 231, 308, 385, 462, 539, 616, 693, 770, 849, 928])
        current_roi = cumulative_savings * progress

        ax5.plot(months[:6], current_roi[:6], marker='o', linewidth=3, markersize=8,
                color=MD3_PRIMARY, markerfacecolor=MD3_SUCCESS, markeredgewidth=2, markeredgecolor=MD3_PRIMARY)
        ax5.fill_between(months[:6], current_roi[:6], alpha=0.3, color=MD3_PRIMARY)
        ax5.set_xlabel('Meses', fontsize=11, fontweight='bold', color='#333333')
        ax5.set_ylabel('Economia USD ($)', fontsize=11, fontweight='bold', color='#333333')
        ax5.set_title('ROI - Economia Acumulada', fontsize=12, fontweight='bold', pad=15, color='#333333')
        ax5.set_xlim(0, 13)
        ax5.set_ylim(0, 1000)
        ax5.grid(True, alpha=0.2)

        # ===== GRÁFICO 6: Distribuição =====
        ax6 = axes[1, 2]
        sizes = [31, 6, 12, 8]
        labels = ['PDF', 'Excel', 'Word', 'EPUB']
        colors_pie = [MD3_PRIMARY, MD3_SECONDARY, MD3_TERTIARY, MD3_SUCCESS]

        if progress > 0.1:
            ax6.pie(sizes, labels=labels, autopct='%1.0f%%', colors=colors_pie,
                   startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold', 'color': '#333333'})
        ax6.set_title('Distribuição de Formatos', fontsize=12, fontweight='bold', pad=15, color='#333333')

        plt.suptitle('MdMax v2.1 - Token Economy Dashboard',
                    fontsize=16, fontweight='bold', y=0.98, color='#333333')

        # Save frame to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=MD3_BG, dpi=100, bbox_inches='tight')
        buf.seek(0)
        image = Image.open(buf)
        frames.append(np.array(image))

    plt.close(fig)

    # Normalizar tamanho de todos os frames
    if frames:
        target_height = frames[0].shape[0]
        target_width = frames[0].shape[1]
        normalized_frames = []
        for frame in frames:
            if frame.shape[0] != target_height or frame.shape[1] != target_width:
                frame = Image.fromarray(frame.astype('uint8'))
                frame = frame.resize((target_width, target_height), Image.Resampling.LANCZOS)
                frame = np.array(frame)
            normalized_frames.append(frame)
        frames = normalized_frames

    # Save as GIF
    output_path = Path('C:/Users/marke/AppData/Roaming/Claude/skills/auto-convert-to-markdown/docs/dashboard-animated.gif')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if frames:
        imageio.mimsave(output_path, frames, duration=50, loop=0)
        print(f"✅ Dashboard animado salvo: {output_path}")
    return output_path

def create_animated_comparison():
    """Create animated workflow comparison"""

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor(MD3_BG)

    frames = []
    num_frames = 80

    for frame in range(num_frames):
        for ax in axes:
            ax.clear()
            ax.set_facecolor(MD3_SURFACE)

        progress = frame / num_frames

        # Antes
        ax_before = axes[0]
        before_data = {'Manual\nWork': 45, 'Formatting': 25, 'Copy/Paste': 20, 'Other': 10}

        # Animar fatias aparecendo
        visible_items = int(len(before_data) * progress)
        if visible_items > 0:
            items = list(before_data.items())[:visible_items]
            data = {k: v for k, v in items}
            if visible_items == len(before_data) and progress < 1:
                # Última fatia animando
                last_value = int(before_data[items[-1][0]] * ((progress - (visible_items-1)/len(before_data)) * len(before_data)))
                data[items[-1][0]] = last_value

            if data:
                colors_before = [MD3_ERROR, MD3_WARNING, MD3_INFO, MD3_SECONDARY][:len(data)]
                wedges, texts, autotexts = ax_before.pie(data.values(), labels=data.keys(),
                                                          autopct='%1.0f%%', colors=colors_before,
                                                          textprops={'fontsize': 11, 'fontweight': 'bold', 'color': '#333333'})

        ax_before.set_title('Workflow Tradicional\n(45 minutos por arquivo)',
                           fontsize=12, fontweight='bold', pad=15, color='#333333')

        # Depois
        ax_after = axes[1]
        after_data = {'Automático': 95, 'Revisão': 5}

        visible_items_after = int(len(after_data) * progress)
        if visible_items_after > 0:
            items_after = list(after_data.items())[:visible_items_after]
            data_after = {k: v for k, v in items_after}

            if data_after:
                colors_after = [MD3_SUCCESS, MD3_SECONDARY][:len(data_after)]
                wedges, texts, autotexts = ax_after.pie(data_after.values(), labels=data_after.keys(),
                                                         autopct='%1.0f%%', colors=colors_after,
                                                         textprops={'fontsize': 11, 'fontweight': 'bold', 'color': '#333333'})

        ax_after.set_title('MdMax Automation\n(<1 minuto com automação)',
                          fontsize=12, fontweight='bold', pad=15, color='#333333')

        plt.suptitle('Transformação do Workflow', fontsize=14, fontweight='bold', y=0.98, color='#333333')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=MD3_BG, dpi=100, bbox_inches='tight')
        buf.seek(0)
        image = Image.open(buf)
        frames.append(np.array(image))

    plt.close(fig)

    # Normalizar tamanho de todos os frames
    if frames:
        target_height = frames[0].shape[0]
        target_width = frames[0].shape[1]
        normalized_frames = []
        for frame in frames:
            if frame.shape[0] != target_height or frame.shape[1] != target_width:
                frame = Image.fromarray(frame.astype('uint8'))
                frame = frame.resize((target_width, target_height), Image.Resampling.LANCZOS)
                frame = np.array(frame)
            normalized_frames.append(frame)
        frames = normalized_frames

    output_path = Path('C:/Users/marke/AppData/Roaming/Claude/skills/auto-convert-to-markdown/docs/workflow-animated.gif')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if frames:
        imageio.mimsave(output_path, frames, duration=50, loop=0)
        print(f"✅ Workflow animado salvo: {output_path}")
    return output_path

if __name__ == '__main__':
    print("🎬 Gerando gráficos animados com Material Design v3...")
    print()
    create_animated_dashboard()
    create_animated_comparison()
    print()
    print("✨ Todos os gráficos animados criados com sucesso!")
