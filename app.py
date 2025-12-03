import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
import os
import io

# --- 1. 基础配置与字体加载 ---
st.set_page_config(page_title="高颜值学术图表生成器", layout="wide")

# 尝试加载本地字体，解决中文乱码问题
@st.cache_resource
def load_font():
    # 优先查找项目目录下的 fonts 文件夹
    font_path = "fonts/SourceHanSerifSC-Regular.ttf" 
    if os.path.exists(font_path):
        font_prop = font_manager.FontProperties(fname=font_path)
        return font_prop
    else:
        # 如果没有找到，回退到默认（可能会乱码，所以建议务必上传字体）
        return None

custom_font = load_font()

# --- 2. 侧边栏：全局设置 ---
st.sidebar.title("🎨 绘图参数设置")

# 数据增强算法（核心需求：让高更高，低更低）
def amplify_data(values, factor):
    """
    数据夸张化处理：
    factor > 1.0 : 拉大差距（强者越强）
    factor = 1.0 : 原始数据
    """
    arr = np.array(values)
    mean_val = np.mean(arr)
    # 以均值为中心向两端拉伸
    amplified = mean_val + (arr - mean_val) * factor
    # 归一化防止越界 (保持在0-100或用户输入的量级范围内，这里做简单截断处理)
    amplified = np.maximum(amplified, 0) 
    return amplified

# --- 3. 主界面：数据录入 ---
st.title("📊 学术汇报专用 - 核心结论可视化工具")
st.markdown("专为大创书、申报书设计。自动优化中文，支持 **300 DPI** 高清导出。")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. 数据输入")
    # 默认数据
    default_data = pd.DataFrame({
        "指标名称": ["创新性", "可行性", "商业价值", "团队基础", "技术壁垒"],
        "数值": [85, 90, 70, 95, 60]
    })
    
    df = st.data_editor(default_data, num_rows="dynamic")
    
    st.subheader("2. 视觉微调")
    # 对比度增强滑块
    contrast_factor = st.slider("⚖️ 观点强化度 (对比度)", 1.0, 3.0, 1.2, 0.1, help="拉大数值差距，突出优势项")
    
    # 颜色设置
    base_color = st.color_picker("选取主色调", "#4E79A7")
    alpha_fill = st.slider("填充透明度", 0.0, 1.0, 0.2)
    
    # 尺寸设置
    chart_style = st.selectbox("图表风格", ["简约雷达图 (推荐)", "普通柱状图"])

with col2:
    st.subheader("3. 实时预览")
    
    # --- 数据处理 ---
    labels = df["指标名称"].tolist()
    raw_values = df["数值"].tolist()
    
    # 应用夸张算法
    final_values = amplify_data(raw_values, contrast_factor)
    
    # --- 绘图逻辑 (Matplotlib) ---
    if chart_style == "简约雷达图 (推荐)":
        # 雷达图需要闭环
        N = len(labels)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1] # 闭环
        
        plot_values = np.concatenate((final_values, [final_values[0]]))
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        # 绘制线条和填充
        ax.plot(angles, plot_values, color=base_color, linewidth=2, linestyle='solid')
        ax.fill(angles, plot_values, color=base_color, alpha=alpha_fill)
        
        # 设置标签 (应用自定义字体)
        if custom_font:
            plt.xticks(angles[:-1], labels, fontproperties=custom_font, size=14)
        else:
            plt.xticks(angles[:-1], labels, size=14)
            
        # 核心需求：隐藏径向数值，只保留网格
        ax.set_yticklabels([]) 
        ax.spines['polar'].set_visible(False) # 隐藏最外圈圆框
        
        # 设置网格线样式
        ax.grid(color='#AAAAAA', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # 动态调整Y轴范围，让图形饱满
        ax.set_ylim(0, max(final_values) * 1.1)

    else:
        # 备用的柱状图
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, final_values, color=base_color, alpha=0.8)
        
        # 隐藏边框，只保留底部
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_yticks([]) # 隐藏Y轴数值
        
        # 标签
        if custom_font:
            plt.xticks(range(len(labels)), labels, fontproperties=custom_font, size=12)
        
        # 在柱子上标数值
        for bar, val in zip(bars, final_values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                    f'{int(val)}', ha='center', va='bottom', fontsize=10)

    st.pyplot(fig)

    # --- 4. 导出逻辑 ---
    st.divider()
    st.subheader("4. 导出高清图")
    
    # 创建内存中的文件缓冲区
    fn = "chart_high_res.png"
    img = io.BytesIO()
    
    # 关键：设置 dpi=300 实现印刷级清晰度
    # bbox_inches='tight' 去除多余白边
    fig.savefig(img, format='png', dpi=300, bbox_inches='tight', transparent=True)
    
    st.download_button(
        label="📥 下载 300 DPI 图片 (透明背景)",
        data=img,
        file_name=fn,
        mime="image/png"
    )
    
    st.caption("提示：'透明背景' 方便直接插入带有背景纹理的 PPT 或 Word 模板中。")