import streamlit as st
import os
import json
import time

# --- 页面基础配置 ---
st.set_page_config(
    page_title="北美建材大零售产品开发系统 (THD & Lowe's SOP V3.0)",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SOP V3.0 核心系统提示词 ---
SOP_SYSTEM_INSTRUCTION = """
你现在担任北美大零售建材产品开发项目经理、资深工业设计分析顾问与结构工程专家。
你必须严格执行《北美建材大零售产品开发与竞品研究 SOP V3.0》（涵盖 The Home Depot 与 Lowe's 标准）。

【核心原则与证据红线】
1. 绝对真实性：严禁捏造数据或把推测当做事实。找不到的一手数据必须明确标记【未找到】或【开发假设】。
2. 动态数据查核：涉及价格、评分、Review 总数、SKU/Item 编码必须以最新网络检索为准，且附带具体日期与有效来源。
3. 尺寸严格解耦：标称开孔尺寸 (Duct Opening)、插入箱体尺寸 (Drop-in Box)、表面面板尺寸 (Faceplate) 必须彻底区分，同时提供英制与毫米 (mm)。
4. 真实 VOC 证据：Review 引用必须基于真实买家反馈，提取高频痛点，不得自行凭空撰写虚假买家评论。
5. 闭环验证：所有 P0 级设计改进必须能够追溯到明确的 VOC 痛点或竞品缺陷，并制定具体的 EVT/DVT 验证方法。
"""

# --- 界面 CSS 增强 ---
st.markdown("""
<style>
    .main-header { font-size: 2.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 0.95rem; color: #475569; margin-bottom: 1.2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 45px; border-radius: 6px 6px 0px 0px; padding: 10px 16px; font-weight: 600; }
    .status-badge { background-color: #E2E8F0; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🛠️ 北美建材大零售产品开发 SOP V3.0 系统</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">整合 The Home Depot (THD) 与 Lowe\'s 渠道标准 | 真实 VOC 溯源 | 结构拆解与制造工艺 | 尺寸绝对解耦</div>', unsafe_allow_html=True)

# --- 侧边栏：模型配置与超丰富启动单 ---
with st.sidebar:
    st.header("⚙️ 引擎配置")
    api_key_input = st.text_input("Gemini API Key", type="password", help="从 Google AI Studio (aistudio.google.com) 获取")
    api_key = api_key_input or os.environ.get("GEMINI_API_KEY", "")
    
    model_name = st.selectbox(
        "模型选择",
        options=["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        index=0,
        help="推荐 gemini-2.5-flash 或 gemini-1.5-pro，具备强大的联网检索与深度推理能力"
    )
    
    temperature = st.slider("严谨度 (Temperature)", min_value=0.0, max_value=0.7, value=0.15, step=0.05, help="保持低数值以防止模型产生幻觉")

    st.markdown("---")
    st.header("📋 V3.0 丰富版项目启动单")
    
    channel_mode = st.selectbox(
        "1. 目标零售渠道*",
        options=["The Home Depot (THD)", "Lowe's", "Dual-Channel (THD + Lowe's 跨渠道对标)"],
        index=0
    )
    
    project_type = st.selectbox(
        "2. 项目核心类型*",
        options=["竞品差评归因与改良", "新品自主定义开发", "Listing 深度优化", "Buyer 选品提案", "成本结构重构", "规格升级"]
    )
    
    product_name = st.text_input("3. 目标品名 (英文 + 中文)*", value="Decorative Floor Register (美标装饰性地板出风口)")
    product_url = st.text_input("4. 目标产品官方链接 / SKU*", value="https://www.homedepot.com/b/Heating-Venting-Cooling-HVAC-Supplies-Registers-Grilles/Floor-Register/N-5yc1vZc4ncZ1z0vj6i")
    
    nominal_size = st.text_input("5. 标称开孔尺寸 (Duct Opening)*", value="4x10 inches (标称管道开口)")
    material_and_finish = st.text_input("6. 预定材质与表面处理", value="重型压铸铝合金 (Cast Aluminum), 哑光黑粉末喷涂")
    load_and_safety = st.text_input("7. 承重与安全规范要求", value="防卡细高跟 (Heel-proof < 9.5mm), 踩踏承重 ≥ 300 lbs")
    
    substrates = st.multiselect(
        "8. 目标安装地材介质",
        options=["实木地板 (Hardwood)", "锁扣地板 (LVP/SPC)", "瓷砖 (Tile)", "地毯 (Carpet)"],
        default=["实木地板 (Hardwood)", "锁扣地板 (LVP/SPC)"]
    )
    
    target_price = st.text_input("9. 目标零售价与成本线 (USD)", value="零售目标: $15.99 - $19.99 | 落地成本: ≤ $3.80")
    competitors = st.text_area("10. 指定竞品对标链接/品牌", value="Accord 4x10 Cast Iron Register; Deflecto Plastic Floor Register")
    focus_points = st.text_area("11. 专项排他约束 / 核心关注痛点", value="1. 重点深挖风门拔片踩断、表面漆膜划伤脱落、与 LVP 地板高差绊脚等高频差评\n2. 拒绝使用易脆化的非阻燃普通塑料做底盒")

# --- 辅助函数 ---
def get_gemini_client(key):
    try:
        from google import genai
        return genai.Client(api_key=key)
    except ImportError:
        st.error("请先安装依赖: `pip install google-genai`")
        return None

def execute_stage(client, model, stage_prompt, stage_name):
    from google.genai import types
    config = types.GenerateContentConfig(
        system_instruction=SOP_SYSTEM_INSTRUCTION,
        temperature=temperature,
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
    with st.spinner(f"正在实时检索并深度执行: {stage_name} ..."):
        try:
            response = client.models.generate_content(
                model=model,
                contents=stage_prompt,
                config=config
            )
            return response.text
        except Exception as e:
            return f"❌ 阶段执行失败: {str(e)}"

# --- 会话状态管理 ---
for i in range(1, 6):
    if f"stage{i}_res" not in st.session_state:
        st.session_state[f"stage{i}_res"] = ""

# --- 启动栏 ---
col_btn, col_info = st.columns([1, 3])
with col_btn:
    run_all_btn = st.button("🚀 启动 SOP V3.0 全流程分析", type="primary", use_container_width=True)
with col_info:
    if not api_key:
        st.info("💡 请先在左侧输入您的 Gemini API Key 即可启动全流程自动化研究。")

# --- 执行主逻辑 ---
if run_all_btn:
    if not api_key:
        st.error("启动失败：缺少 Gemini API Key，请在左侧侧边栏配置。")
    elif not product_name or not nominal_size or not product_url:
        st.error("启动失败：启动单中的品名、开孔尺寸、产品链接为必填项。")
    else:
        client = get_gemini_client(api_key)
        if client:
            context_header = f"""
【SOP V3.0 启动单输入参数】
- 目标渠道: {channel_mode}
- 项目类型: {project_type}
- 产品名称: {product_name}
- 官方详情页链接 / 标识: {product_url}
- 标称风管开孔尺寸 (Duct Opening): {nominal_size}
- 材质与表面处理: {material_and_finish}
- 承重与物理安全: {load_and_safety}
- 目标安装地材: {', '.join(substrates)}
- 目标价格与成本线: {target_price}
- 指定对标竞品: {competitors}
- 核心关注痛点与约束: {focus_points}
"""

            # --- 阶段 1 ---
            p1 = f"""{context_header}
请严格执行《SOP V3.0》的【Stage 1: 物理架构与规格基准库】（涵盖 Node 00, 00.5, 01, 02）：
1. 【00 & 00.5 项目章程与渠道界定】：明确在 {channel_mode} 渠道下的准入要求、业务目标与非目标范围。
2. 【01 产品基础规格拆解库】：
   - 联网检索并抓取目标产品真实参数（售价、当前评分、Review总数、推荐率、质保期、产地）。
   - 强制三维尺寸解耦：标称开孔尺寸 (Duct Opening)、插入箱体外径及公差 (Drop-in Box)、表面面板尺寸与厚度 (Faceplate)。
   - 建立结构化【Product Specification Database】Markdown 表格。
3. 【02 渠道产品定位】：分析其在 {channel_mode} 货架上的生态位，拆解 Functional / Economic / Emotional 三重价值。
严格标注证据等级（【FACT】/【INFERENCE】等），禁止编造虚假尺寸。
"""
            st.session_state.stage1_res = execute_stage(client, model_name, p1, "Stage 1 物理架构与规格库")

            # --- 阶段 2 ---
            p2 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 2: 场景矩阵、适配性与真实 VOC 挖掘】（涵盖 Node 03, 04, 05, 05.5）：
1. 【03 真实四维场景矩阵】：空间功能区 × 4大地材介质（实木、LVP、瓷砖、地毯）× 踩踏负荷 × 冷热循环工况。
2. 【04 适配性与安装干涉矩阵】：针对标准美标钣金风管与不同地材厚度的适配状态（✓ Compatible / △ Conditional / ✕ Not Compatible）。禁止使用 "Fits All"！
3. 【05 真实买家 VOC 深度挖掘】：真实联网检索并提取 1~5 星评论与 Q&A。归纳出 Positive VOC、Negative VOC（安装难、异响、踩塌、划痕、漏风等）。
4. 【05.5 竞品 VOC 对标分析】：对比参考竞品（{competitors}），分析哪些差评是行业通病，哪些是该款特有缺陷。
"""
            st.session_state.stage2_res = execute_stage(client, model_name, p2, "Stage 2 场景适配与 VOC 挖掘")

            # --- 阶段 3 ---
            p3 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 3: 根因归因、结构拆解与制造工艺】（涵盖 Node 06, 07, 07.5）：
1. 【06 差评根因归因链 (Root Cause)】：建立链条：买家抱怨 (Complaint) → 物理表象 (Symptom) → 根因 (Root Cause) → 归类（设计缺陷 / 制造缺陷 / 信息虚标 / 用户误用）。
2. 【07 物理结构拆解 (Teardown)】：拆解 面板、底盒、风门导流片、调节手柄、铰链轴等核心零部件。指出薄弱应力集中点。
3. 【07.5 制造工艺与质量风险】：分析材料选型、成型工艺（如压铸铝 vs 冲压铁）、涂装工艺及常见瑕疵（毛刺、翘曲、缩水、盐雾生锈）。
"""
            st.session_state.stage3_res = execute_stage(client, model_name, p3, "Stage 3 根因归因与结构制造")

            # --- 阶段 4 ---
            p4 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 4: 商业数据库、机会排序与下一代产品定义】（涵盖 Node 08, 09, 09.5, 10, 11, 11.5, 12, 13, 14）：
1. 【08-09 竞品与规格数据库】：建立包含 EXACT, DIRECT, GENERIC, BENCHMARK 的多竞品对比表（含零售价、评分、核心卖点）。
2. 【09.5 成本结构测算】：估算 BOM 材料、表面喷涂、装配包装、海运落地成本，评估毛利率。
3. 【10 相似度量化评分】：制定权重矩阵，对关键竞品进行 0-100 分相似度打分。
4. 【11-12 痛点排序与设计机会】：将痛点按频次与致命度排序，建立 `VOC → 根因 → 机会 → 工业设计改进` 的闭环。
5. 【13-14 下一代产品定义与 P0/P1/P2】：明确下一代改进型产品的物理参数、非妥协 Must-Have (P0)、体验升级 Should-Have (P1) 与差异化 (P2)。
"""
            st.session_state.stage4_res = execute_stage(client, model_name, p4, "Stage 4 机会矩阵与下一代定义")

            # --- 阶段 5 ---
            p5 = f"""{context_header}
基于全部前期调研成果，请严格执行《SOP V3.0》的【Stage 5: 验证计划、渠道专属 Listing 与 20 问终极闭环】（涵盖 Node 15, 16, 17, 18）：
1. 【15 EVT / DVT / PVT 工程测试计划】：建立完整的工程验证矩阵（承重测试方法、防卡跟治具、盐雾试验时长、验收标准、绝不可随意写虚假 PASS）。
2. 【16 {channel_mode} 专属 Listing 策略】：
   - 符合该零售平台算法的 Product Title
   - Compatibility-First 核心 5 点特征 Bullet Points
   - 避免退货的尺寸/地材兼容性提示图文说明指南 (Compatibility Guide)
3. 【17 终版产品定义书 (Final Definition)】：系统提炼最终工程规格卡片。
4. 【18 终极闭环：解答 20 个产品开发核心决策问题】：逐一精确作答 20 个决策问题，为产品经理、结构工程师与海外买手提供立即可用的定论。
"""
            st.session_state.stage5_res = execute_stage(client, model_name, p5, "Stage 5 验证计划与 20 问闭环")
            st.success("🎉 《北美建材大零售产品开发 SOP V3.0》全流程深度研究已执行完毕！")

# --- 结果展示与下载 Tab ---
if any(st.session_state[f"stage{i}_res"] for i in range(1, 6)):
    tab1, tab2, tab3, tab4, tab5, tab_full = st.tabs([
        "📐 Stage 1: 物理规格库",
        "🏡 Stage 2: 场景与真实 VOC",
        "🔬 Stage 3: 根因与结构拆解",
        "💡 Stage 4: 机会与下一代定义",
        "🎯 Stage 5: 验证计划与 Listing",
        "📄 完整报告总览与下载"
    ])
    
    with tab1:
        st.markdown(st.session_state.stage1_res)
    with tab2:
        st.markdown(st.session_state.stage2_res)
    with tab3:
        st.markdown(st.session_state.stage3_res)
    with tab4:
        st.markdown(st.session_state.stage4_res)
    with tab5:
        st.markdown(st.session_state.stage5_res)
    with tab_full:
        full_content = f"""# {product_name} - 北美大零售产品开发深度调研报告 (SOP V3.0)
- 目标渠道: {channel_mode}
- 报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
- 标称开孔尺寸: {nominal_size}
- 目标参考链接: {product_url}

---
## 【Stage 1: 物理架构与规格基准库】
{st.session_state.stage1_res}

---
## 【Stage 2: 场景矩阵、适配性与真实 VOC 挖掘】
{st.session_state.stage2_res}

---
## 【Stage 3: 根因归因、结构拆解与制造工艺】
{st.session_state.stage3_res}

---
## 【Stage 4: 商业数据库、机会排序与下一代产品定义】
{st.session_state.stage4_res}

---
## 【Stage 5: 验证计划、渠道专属 Listing 与 20 问终极闭环】
{st.session_state.stage5_res}
"""
        st.markdown(full_content)
        st.download_button(
            label="📥 一键下载完整研究报告 (.md)",
            data=full_content,
            file_name=f"THD_Lowes_SOP_V3_{nominal_size.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
