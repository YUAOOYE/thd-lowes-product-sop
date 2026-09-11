import streamlit as st
import os
import json
import time
import re

# ==============================================================================
# 0. 本地历史存档目录初始化
# ==============================================================================
HISTORY_DIR = "history_projects"
os.makedirs(HISTORY_DIR, exist_ok=True)

# ==============================================================================
# 1. 页面配置与主题样式
# ==============================================================================
st.set_page_config(
    page_title="北美建材大零售产品开发系统 (THD & Lowe's SOP V3.0)",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 0.95rem; color: #475569; margin-bottom: 1.2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 45px; border-radius: 6px 6px 0px 0px; padding: 10px 16px; font-weight: 600; }
    .stage-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🛠️ 北美建材大零售产品开发 SOP V3.0 系统</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">多模型引擎联动 (Gemini / WorkBuddy / OpenAI / Claude / DeepSeek) | 503 过载自动重试与智能切模 | 真实网络证据闭环 | 结构拆解与制造工艺</div>', unsafe_allow_html=True)

def render_safe_markdown(text: str):
    """防止电商价格 $ 符号被误识别为 KaTeX 数学公式导致排版变形"""
    if not text:
        return
    safe_text = re.sub(r'(?<!\\)\$(\d)', r'\\$\1', text)
    st.markdown(safe_text, unsafe_allow_html=True)

# ==============================================================================
# 2. SOP V3.0 核心系统提示词
# ==============================================================================
SOP_SYSTEM_INSTRUCTION = """
你现在担任北美大零售建材产品开发项目经理、资深工业设计分析顾问与结构工程专家。
你必须严格执行《北美建材大零售产品开发与竞品研究 SOP V3.0》（涵盖 The Home Depot 与 Lowe's 标准）。

【核心原则与四大红线】
1. 绝对真实性：所有数据必须依据提供的最新检索事实进行提炼。严禁捏造虚假参数。
2. 动态数据必须包含：当前市场售价区间、实际评分、评价数量级、官方产品代码（如 Home Depot Internet # / Store SKU，Lowe's Item #）。
3. 尺寸严格解耦与通俗讲透：标称安装尺寸/管径 (Nominal / Cutout)、插入配合部尺寸 (Drop-in / Body)、外沿法兰盘/面板尺寸 (Faceplate / Flange) 必须彻底区分，同时提供英制与公制毫米 (mm)。

4. 【去官方化与说大白话红线（拒绝假大空与学术八股）】：
   - 彻底摒弃官方晦涩套话、机械术语与空洞长句。
   - 全程使用一线业务员、现场安装师傅或普通买家一秒能懂的“通俗大白话 / 人话”进行讲解。
   - 必须针对当前启动单指定的【具体实体产品】进行专属拆解，严禁张冠李戴，严禁把其他品类的结构生搬硬套到非对应产品上！
   - 关键概念根据当前产品直白翻译：
     * 尺寸：讲清“量哪里别买错！外径多大、内径多大、孔位多大、公差多少”。
     * 承重与受力：讲清“受压、扭紧、踩踏时会不会破裂、会不会断裂、会不会脱扣”。
     * 密封与耐候：讲清“会不会漏水、会不会老化脆化、防不防锈”。
   - 结论先行，杜绝冗长废话铺垫。

5. 【中英文双语对照与实体产品地道英文红线 (Product-Grounded Bilingual English)】：
   - 必须严格结合当前【具体物理实体产品】以及北美建材商超（The Home Depot / Lowe's）官方标准货架术语：
     * 格式统一：【中文通俗白话 (真实北美行业/实体产品一手英文术语 Native Trade & Retail Term)】。
     * 严禁机械生硬机翻，严禁通用词直译，严禁将其他产品的专用部件名称错误移植到当前产品。
   - 商业与 Listing 英文：
     * 标题与卖点必须符合北美大零售平台搜索算法与真实买家搜索习惯（High-converting Search Terms），严禁中式英语语法。

6. 【图文对照红线】：
   - 在解释产品物理结构、部位名称、测量方法、缺陷痛点以及下一代设计方案时，按需嵌入对应的【产品实际部位图、结构测量图或设计样品图】Markdown 链接。
   - 优先从输入单提供的【产品部位图与样品图链接库】中调用。若输入库与当前产品不符，则不要强行关联。

7. 【真实性证据链与必须提供可核验超链接红线 (Zero-Hallucination & Mandatory Hyperlinks)】：
   - 绝对杜绝空洞臆造与误导性假信息：严禁捏造具体售价、虚构买家评分、凭空编造 SKU 编码或伪造测试合格结论！
   - 所有关于市场价格区间、买家真实吐槽原声、工程认证标准（ASTM / IBC / ADA 等）与竞品对比的核心观点，必须尽可能紧随其后附带可点击验证的 Markdown 超链接，格式为：`[来源名称/页面](https://...)`。
   - 查不到时诚实标注：若某项具体参数在公开网络无法检索确认，严禁凭空臆测，必须明确标明 `【未找到公开源】` 或 `【公开数据无法验证】`，向用户披露不确定性，绝不提供看似真实实则误导的虚假信息！

8. 闭环验证：所有 P0 级设计改进必须能够追溯到明确的 VOC 痛点或竞品缺陷，并制定具体的 EVT/DVT/PVT 验证方法。
"""

# ==============================================================================
# 3. 模型配置映射字典 (首选 gemini-2.0-flash: 算力最充裕，极低 503 概率)
# ==============================================================================
PROVIDER_MODELS = {
    "Google Gemini": [
        "gemini-2.0-flash (经典高稳定极速版: 算力池大，推荐首选)",
        "gemini-1.5-flash (长效高并发主力: 极少过载)",
        "gemini-2.5-flash (2026官方高智能极速版)",
        "gemini-2.5-pro (前沿深度推理旗舰)",
        "gemini-1.5-pro (长上下文与深度逻辑旗舰)",
        "gemini-flash-latest (动态指向最新稳定版)"
    ],
    "WorkBuddy (腾讯云 AI Agent)": [
        "deepseek-reasoner (DeepSeek-R1 深度思考推理大模型)",
        "deepseek-chat (DeepSeek-V3 办公与分析主力模型)",
        "hunyuan-pro (腾讯混元深度思考与通用旗舰)",
        "hunyuan-standard (腾讯混元标准版: 极速低耗)",
        "claude-3-7-sonnet (混合推理旗舰: 强逻辑与混合思考)",
        "gpt-4o (全能旗舰多模态: 均衡首选)"
    ],
    "OpenAI (ChatGPT)": [
        "gpt-4o (全能旗舰: 速度、多模态与工程解析平衡首选)",
        "gpt-4o-mini (极速高性价比工作流)",
        "o3-mini (最新高能效深度推理模型 / 思考链)",
        "o1 (旗舰级深度推理大模型)",
        "chatgpt-4o-latest (始终指向ChatGPT最新动态版)"
    ],
    "Anthropic Claude": [
        "claude-3-7-sonnet-20250219 (最新混合推理旗舰: 强逻辑与混合思考)",
        "claude-3-5-sonnet-20241022 (工程级公认最强代码与结构拆解)",
        "claude-3-5-haiku-20241022 (极速轻量低延迟)"
    ],
    "DeepSeek (深度求索)": [
        "deepseek-chat (DeepSeek-V3 通用主力: 极高性价比与强中文理解)",
        "deepseek-reasoner (DeepSeek-R1 旗舰推理: 显式思考链分析)"
    ],
    "OpenAI 兼容中转 / OpenRouter / 自定义 API": [
        "deepseek-ai/DeepSeek-V3",
        "deepseek-ai/DeepSeek-R1",
        "anthropic/claude-3.7-sonnet",
        "openai/gpt-4o"
    ]
}

FALLBACK_MODELS = {
    "Google Gemini": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"],
    "WorkBuddy (腾讯云 AI Agent)": ["deepseek-chat", "deepseek-reasoner", "hunyuan-pro", "gpt-4o"],
    "DeepSeek (深度求索)": ["deepseek-chat", "deepseek-reasoner"],
    "OpenAI (ChatGPT)": ["gpt-4o-mini", "gpt-4o", "o3-mini"],
    "Anthropic Claude": ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"]
}

def is_transient_error(err_str):
    """判断是否为 Google / OpenAI 服务器临时负载波动"""
    transient_keywords = [
        "503", "overload", "unavailable", "server is busy", "502", "504", 
        "rate limit", "temporarily", "429", "resource_exhausted", "capacity", 
        "timeout", "servererror", "server error", "500", "internal error"
    ]
    return any(k in str(err_str).lower() for k in transient_keywords)

def is_model_not_found_error(err_str):
    not_found_keywords = ["not found", "404", "invalid argument", "unsupported model", "permission denied", "not supported for generatecontent", "does not exist"]
    return any(k in str(err_str).lower() for k in not_found_keywords)

def live_web_search(query, max_results=3):
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get('title', '').strip()
                href = r.get('href', '').strip()
                body = r.get('body', '').strip()[:300]
                results.append(f"【来源: {title}】({href}):\n{body}")
        return "\n\n".join(results)[:1500]
    except Exception:
        return ""

# ==============================================================================
# 4. 底层接口与辅助函数定义
# ==============================================================================
def call_single_attempt(provider_name, api_key_val, model_id, final_prompt, base_url_val="", temp_val=0.1, system_inst=SOP_SYSTEM_INSTRUCTION, enable_search=True):
    """底层通用单次模型请求"""
    if provider_name == "Google Gemini":
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key_val)
            
            config_args = {
                "temperature": temp_val
            }
            if system_inst:
                config_args["system_instruction"] = system_inst
            if enable_search:
                config_args["tools"] = [types.Tool(google_search=types.GoogleSearch())]
                
            try:
                config = types.GenerateContentConfig(**config_args)
                response = client.models.generate_content(
                    model=model_id,
                    contents=final_prompt,
                    config=config
                )
            except Exception:
                # 容错降级：移除 tools 再次尝试
                config_args.pop("tools", None)
                config = types.GenerateContentConfig(**config_args)
                response = client.models.generate_content(
                    model=model_id,
                    contents=final_prompt,
                    config=config
                )

            res_text = response.text or ""
            grounding_links = []
            try:
                if hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, "grounding_metadata") and candidate.grounding_metadata:
                        gm = candidate.grounding_metadata
                        if hasattr(gm, "grounding_chunks") and gm.grounding_chunks:
                            for chunk in gm.grounding_chunks:
                                if hasattr(chunk, "web") and chunk.web:
                                    t = getattr(chunk.web, "title", "") or "权威官方参考源"
                                    u = getattr(chunk.web, "uri", "")
                                    if u and u.startswith("http") and u not in [l[1] for l in grounding_links]:
                                        grounding_links.append((t, u))
            except Exception:
                pass

            if grounding_links:
                res_text += "\n\n---\n**🔗 Google 官方实时检索核验来源 (点击可直接验证):**\n"
                for title, uri in grounding_links[:6]:
                    res_text += f"- [{title}]({uri})\n"

            return res_text
        except ImportError:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=api_key_val)
            model = legacy_genai.GenerativeModel(model_name=model_id, system_instruction=system_inst)
            res = model.generate_content(final_prompt, generation_config={"temperature": temp_val})
            return res.text

    elif provider_name in ["WorkBuddy (腾讯云 AI Agent)", "OpenAI (ChatGPT)", "DeepSeek (深度求索)", "OpenAI 兼容中转 / OpenRouter / 自定义 API"]:
        import openai
        if provider_name == "WorkBuddy (腾讯云 AI Agent)":
            client = openai.OpenAI(api_key=api_key_val, base_url=base_url_val or "https://api.workbuddy.cn/v1", timeout=120.0)
        elif provider_name == "DeepSeek (深度求索)":
            client = openai.OpenAI(api_key=api_key_val, base_url="https://api.deepseek.com", timeout=120.0)
        elif provider_name == "OpenAI 兼容中转 / OpenRouter / 自定义 API":
            client = openai.OpenAI(api_key=api_key_val, base_url=base_url_val or "https://openrouter.ai/api/v1", timeout=120.0)
        else:
            client = openai.OpenAI(api_key=api_key_val, timeout=120.0)

        is_reasoner = any(k in model_id.lower() for k in ["o1", "o3", "reasoner"])
        is_openai_official_reasoner = ("o1" in model_id.lower() or "o3" in model_id.lower()) and (provider_name == "OpenAI (ChatGPT)")

        if is_reasoner:
            messages = [
                {"role": "user", "content": f"【系统指导准则】\n{system_inst}\n\n【当前分析任务】\n{final_prompt}"}
            ]
            token_key = "max_completion_tokens" if is_openai_official_reasoner else "max_tokens"
            call_args = {"model": model_id, "messages": messages, token_key: 8192}
        else:
            messages = [
                {"role": "system", "content": system_inst},
                {"role": "user", "content": final_prompt}
            ]
            call_args = {"model": model_id, "messages": messages, "temperature": temp_val, "max_tokens": 8192}

        res = client.chat.completions.create(**call_args)
        return res.choices[0].message.content

    elif provider_name == "Anthropic Claude":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key_val, timeout=120.0)
        res = client.messages.create(
            model=model_id,
            system=system_inst,
            max_tokens=8192,
            temperature=temp_val,
            messages=[{"role": "user", "content": final_prompt}]
        )
        return res.content[0].text
    else:
        raise ValueError(f"未受支持的供应商: {provider_name}")

def parse_url_to_launchpad(quick_input, provider_name, api_key_val, model_id, base_url_val=""):
    """输入产品链接或品名/SKU，带高可用容错与备选模型自动切换"""
    search_query = f"{quick_input} product specifications dimensions materials price home depot lowes"
    fetched_web = live_web_search(search_query, max_results=3)
    
    parsing_prompt = f"""
你是一名北美大零售（The Home Depot / Lowe's）资深产品总监与工程选品专家。
目标输入信息：【{quick_input}】。

【参考联网检索信息】：
{fetched_web}

请严格按下列格式输出合法的纯 JSON 字典，切勿包含代码块标记外的任何多余文字：
{{
  "channel": "严格从列表匹配一个：['The Home Depot (THD)', 'Lowe\\'s', 'Dual-Channel (THD + Lowe\\'s 跨渠道对标)']",
  "product_name": "完整品名，中英双语",
  "product_url": "{quick_input}",
  "nominal_size": "标称安装开孔/尺寸基准 (含英制与公制)",
  "material_and_finish": "真实材质与表面工艺",
  "load_and_safety": "行业承重与安全规范",
  "mounting_type": "安装部位，严格从列表匹配一个：['厨卫/橱柜/台面/管道 (Kitchen, Bath & Plumbing)', '地面安装 (Floor)', '墙面/天花板安装 (Wall & Ceiling)', '门窗/出入口五金 (Doors & Hardware)', '户外/甲板/庭院 (Outdoor & Deck)', '独立放置/免安装 (Freestanding/Portable)']",
  "target_persona": "目标客群，从列表匹配一个：['全客群通用 (DIY房主 + PRO承包商双轮驱动)', '聚焦 DIY 个人房主 (极简安装与防呆)', '聚焦 PRO 专业施工承包商 (快速作业与耐操耐久)']",
  "packaging_type": "零售包装形态，从列表匹配一个：['热缩膜带展示卡 (Shrink Wrap w/ Header Card) - 经济畅销型', '双面高透吸塑泡壳 (Clamshell Blister Pack) - 防盗抗撕挂钩型', '独立开窗瓦楞彩盒 (Corrugated Box w/ Window) - 高端防摔防护型', '工程批发大包装 (Contractor Bulk Pack) - 工地大宗出货型']",
  "included_accessories": "随附配件与紧固件",
  "target_price": "市场零售价与落地成本",
  "competitors": "Top 2 核心主流竞品",
  "focus_points": "买家最痛的 3 大真实差评吐槽与新人避坑重点"
}}
"""
    # 建立候选模型池，防止主模型 503 导致失败
    candidate_models = [model_id]
    if provider_name in FALLBACK_MODELS:
        for fb in FALLBACK_MODELS[provider_name]:
            if fb != model_id and fb not in candidate_models:
                candidate_models.append(fb)

    raw_res = ""
    for current_model in candidate_models[:3]:
        for attempt in range(1, 3):
            try:
                # 预填使用轻量指令，且禁用二次 Google Tools，极大降低 500/503 几率
                raw_res = call_single_attempt(
                    provider_name=provider_name,
                    api_key_val=api_key_val,
                    model_id=current_model,
                    final_prompt=parsing_prompt,
                    base_url_val=base_url_val,
                    temp_val=0.1,
                    system_inst="You are a professional product spec extractor. Output valid JSON only.",
                    enable_search=False
                )
                if raw_res:
                    break
            except Exception as e:
                err_str = str(e)
                if is_model_not_found_error(err_str):
                    break
                time.sleep(attempt * 1.5)
        if raw_res:
            break

    if not raw_res:
        return None

    match = re.search(r'\{.*\}', raw_res, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return None

def get_accumulated_context(current_stage_idx: int) -> str:
    """提取当前阶段之前所有阶段的结论精华，实现流水线滚动记忆闭环"""
    if current_stage_idx == 1:
        return ""
    summary_parts = []
    for i in range(1, current_stage_idx):
        res = st.session_state.get(f"stage{i}_res", "").strip()
        if res and not res.startswith("❌"):
            summary_parts.append(f"=== 【前序 Stage {i} 已锁定的调研结论】 ===\n{res[:1500]}")
    if summary_parts:
        return "\n\n【核心上下文记忆库（必须基于以下前序已锁定事实演进，严禁前后矛盾）】:\n" + "\n\n".join(summary_parts)
    return ""

def execute_stage(provider_name, api_key_val, model_id, stage_prompt, stage_name, search_query="", base_url_val="", temp_val=0.1, extra_data=""):
    realtime_context = ""
    if search_query:
        with st.spinner(f"正在实时抓取一手网络数据: {search_query[:35]} ..."):
            fetched_data = live_web_search(search_query)
            if fetched_data:
                realtime_context = f"\n\n【最新互联网实时抓取证据库】:\n{fetched_data}\n"
    
    if extra_data.strip():
        realtime_context += f"\n\n【用户补充事实库】:\n{extra_data.strip()}\n"

    final_prompt = stage_prompt + realtime_context

    candidate_models = [model_id]
    if provider_name in FALLBACK_MODELS:
        for fb in FALLBACK_MODELS[provider_name]:
            if fb != model_id and fb not in candidate_models:
                candidate_models.append(fb)

    last_err = ""
    status_bar = st.empty()
    
    for current_model in candidate_models[:3]:
        for attempt in range(1, 3):
            with st.spinner(f"⚡ 正在执行: {stage_name} (模型: `{current_model}`)..."):
                try:
                    result = call_single_attempt(
                        provider_name=provider_name,
                        api_key_val=api_key_val,
                        model_id=current_model,
                        final_prompt=final_prompt,
                        base_url_val=base_url_val,
                        temp_val=temp_val,
                        system_inst=SOP_SYSTEM_INSTRUCTION,
                        enable_search=True
                    )
                    status_bar.empty()
                    if current_model != model_id:
                        st.caption(f"💡 注：主模型遇波峰，此阶段已通过备用模型 `{current_model}` 成功生成。")
                    return result
                except Exception as e:
                    last_err = str(e)
                    if is_model_not_found_error(last_err):
                        status_bar.info(f"🔄 模型 `{current_model}` 不可用，自动切至下一备选...")
                        break
                    elif is_transient_error(last_err):
                        wait_sec = attempt * 3
                        status_bar.info(f"⏳ `{current_model}` 流量高峰 (ServerError)，退避重试 ({attempt}/2，等待 {wait_sec}s)...")
                        time.sleep(wait_sec)
                    else:
                        status_bar.empty()
                        return f"❌ 阶段执行遇到异常: {last_err}"
        
        status_bar.info(f"🔄 模型 `{current_model}` 繁忙，自动切至备用模型...")
        time.sleep(1.0)

    status_bar.empty()
    return f"❌ 阶段执行失败：模型服务繁忙 (ServerError)，请在下方点击【🔄 重新运行】重试。\n错误原因: {last_err}"

def save_project_to_disk(prod_name, ch_mode):
    if not prod_name:
        return
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\u4e00-\u9fa5]', '_', prod_name)[:40]
    file_path = os.path.join(HISTORY_DIR, f"{clean_name}.json")
    save_data = {
        "product_name": prod_name,
        "saved_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "channel": ch_mode,
        "stages": {f"stage{i}_res": st.session_state.get(f"stage{i}_res", "") for i in range(1, 7)}
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

# 初始化状态
for i in range(1, 7):
    if f"stage{i}_res" not in st.session_state:
        st.session_state[f"stage{i}_res"] = ""

# ==============================================================================
# 5. 侧边栏：多模型配置与启动单输入
# ==============================================================================
with st.sidebar:
    st.header("⚙️ 多模型引擎配置")
    
    provider = st.selectbox("选择 API 供应商*", options=list(PROVIDER_MODELS.keys()), index=0)
    
    env_map = {
        "Google Gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "WorkBuddy (腾讯云 AI Agent)": ["WORKBUDDY_API_KEY", "CODEBUDDY_API_KEY", "OPENAI_API_KEY"],
        "OpenAI (ChatGPT)": ["OPENAI_API_KEY"],
        "Anthropic Claude": ["ANTHROPIC_API_KEY"],
        "DeepSeek (深度求索)": ["DEEPSEEK_API_KEY", "OPENAI_API_KEY"],
        "OpenAI 兼容中转 / OpenRouter / 自定义 API": ["OPENROUTER_API_KEY", "OPENAI_API_KEY"]
    }
    
    matched_key = ""
    for env_k in env_map.get(provider, []):
        if hasattr(st, "secrets") and env_k in st.secrets:
            matched_key = st.secrets[env_k]
            break
        elif os.environ.get(env_k):
            matched_key = os.environ.get(env_k)
            break

    api_key_label = f"{provider.split(' ')[0]} API Key*"
    api_key = st.text_input(api_key_label, value=matched_key, type="password", help=f"请输入 {provider} 的访问凭证")
    
    custom_base_url = ""
    if provider == "WorkBuddy (腾讯云 AI Agent)":
        custom_base_url = st.text_input("WorkBuddy API Base URL*", value="https://api.workbuddy.cn/v1")
    elif provider == "OpenAI 兼容中转 / OpenRouter / 自定义 API":
        custom_base_url = st.text_input("自定义 API Base URL*", value="https://openrouter.ai/api/v1")
    elif provider == "DeepSeek (深度求索)":
        custom_base_url = "https://api.deepseek.com"

    if f"dynamic_models_{provider}" not in st.session_state:
        st.session_state[f"dynamic_models_{provider}"] = list(PROVIDER_MODELS[provider])

    current_models = list(st.session_state[f"dynamic_models_{provider}"])
    if "自定义模型名称 (手动输入...)" not in current_models:
        current_models.append("自定义模型名称 (手动输入...)")

    col_m1, col_m2 = st.columns((3, 1))
    with col_m1:
        selected_model_option = st.selectbox(f"选择模型 ({provider.split(' ')[0]} 专属)", options=current_models, index=0)
    with col_m2:
        if provider == "Google Gemini":
            if st.button("🔄 刷新", help="在线拉取官方最新可用模型"):
                if not api_key:
                    st.warning("请先填入 Key")
                else:
                    try:
                        from google import genai
                        temp_client = genai.Client(api_key=api_key)
                        fetched = [m.name.replace("models/", "") for m in temp_client.models.list() if "gemini" in str(m).lower()]
                        if fetched:
                            merged = sorted(list(set(fetched + [m.split(" ")[0] for m in PROVIDER_MODELS["Google Gemini"]])), reverse=True)
                            st.session_state[f"dynamic_models_{provider}"] = merged
                            st.success(f"已同步 {len(fetched)} 个模型！")
                            st.rerun()
                    except Exception as e:
                        st.error(f"同步失败: {str(e)[:25]}")
    
    if "自定义模型名称" in selected_model_option:
        default_custom = "gemini-2.0-flash" if "Gemini" in provider else ("deepseek-chat" if "WorkBuddy" in provider or "DeepSeek" in provider else "gpt-4o")
        model_name = st.text_input("请输入具体模型 ID:", value=default_custom)
    else:
        model_name = selected_model_option.split(" ")[0].strip()
        
    st.caption(f"当前生效模型: `{model_name}`")
    
    temperature = st.slider("严谨度 (Temperature)", min_value=0.0, max_value=0.5, value=0.1, step=0.05)

    existing_records = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    if existing_records:
        st.markdown("---")
        st.markdown("##### 📂 历史调研项目快速调取")
        selected_hist = st.selectbox("选择以往存档", ["-- 选择已保存的产品报告 --"] + existing_records)
        if selected_hist != "-- 选择已保存的产品报告 --" and st.button("📥 一键载入所选报告", use_container_width=True):
            with open(os.path.join(HISTORY_DIR, selected_hist), "r", encoding="utf-8") as f:
                hist_data = json.load(f)
                for k, v in hist_data.get("stages", {}).items():
                    st.session_state[k] = v
                st.session_state["analyzed_product_name"] = hist_data.get("product_name", "")
                st.session_state["p_name"] = hist_data.get("product_name", "")
                st.success(f"已恢复【{hist_data.get('product_name')}】的分析结果！")
                st.rerun()

    st.markdown("---")
    st.header("📋 V3.0 丰富版项目启动单")

    with st.container():
        st.markdown("##### 🪄 新人智能助手：链接一键预填")
        st.caption("粘贴产品官网链接、SKU 或英文品名，AI 将自动联网提炼并填好启动单参数。")
        col_q1, col_q2 = st.columns((3, 2))
        with col_q1:
            quick_input = st.text_input("产品链接/SKU", value="", placeholder="粘贴 THD/Lowe's 链接或品名...", label_visibility="collapsed")
        with col_q2:
            parse_click = st.button("⚡ 智能填入启动单", type="primary", use_container_width=True)

        if parse_click:
            if not api_key:
                st.error("请先在上方输入 API Key！")
            elif not quick_input.strip():
                st.warning("请先粘贴产品链接或输入产品名称！")
            else:
                try:
                    with st.spinner("🔍 正在检索官方详情页并提炼工程规格 (遇繁忙将自动切备选)..."):
                        parsed_res = parse_url_to_launchpad(quick_input.strip(), provider, api_key, model_name, custom_base_url)
                        if parsed_res:
                            st.session_state["p_channel"] = parsed_res.get("channel", "The Home Depot (THD)")
                            st.session_state["p_name"] = parsed_res.get("product_name", "")
                            st.session_state["p_url"] = parsed_res.get("product_url", quick_input.strip())
                            st.session_state["p_size"] = parsed_res.get("nominal_size", "")
                            st.session_state["p_mat"] = parsed_res.get("material_and_finish", "")
                            st.session_state["p_load"] = parsed_res.get("load_and_safety", "")
                            st.session_state["p_mount"] = parsed_res.get("mounting_type", "地面安装 (Floor)")
                            st.session_state["p_persona"] = parsed_res.get("target_persona", "全客群通用 (DIY房主 + PRO承包商双轮驱动)")
                            st.session_state["p_pkg"] = parsed_res.get("packaging_type", "热缩膜带展示卡 (Shrink Wrap w/ Header Card) - 经济畅销型")
                            st.session_state["p_acc"] = parsed_res.get("included_accessories", "")
                            st.session_state["p_price"] = parsed_res.get("target_price", "")
                            st.session_state["p_comp"] = parsed_res.get("competitors", "")
                            st.session_state["p_focus"] = parsed_res.get("focus_points", "")
                            st.success("🎉 已智能解析并填入启动单！可随时审阅和修改。")
                            time.sleep(0.8)
                            st.rerun()
                        else:
                            st.warning("⚠️ 官方接口当前负载偏高 (ServerError)，未完成自动提取。请您直接在下方输入框手动填写。")
                except Exception as err:
                    st.warning(f"⚠️ 智能解析遇到服务器临时波动，已为您保留输入框，请直接在下方手动输入。")

    with st.expander("💡 快速填入示例产品模板 (可选)"):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("📦 载入【地板出风口 4x10】"):
                st.session_state["p_channel"] = "The Home Depot (THD)"
                st.session_state["p_name"] = "Decorative Floor Register (美标装饰性地板出风口 4x10)"
                st.session_state["p_url"] = "https://www.homedepot.com/b/Heating-Venting-Cooling-HVAC-Supplies-Registers-Grilles/Floor-Register/N-5yc1vZc4ncZ1z0vj6i"
                st.session_state["p_size"] = "4x10 inches (标称风管开孔)"
                st.session_state["p_mat"] = "重型铸铝 (Cast Aluminum) / 哑光黑粉末喷涂 (Matte Black)"
                st.session_state["p_load"] = "承重 >= 300 lbs, 防卡安全孔隙 < 9.5 mm"
                st.session_state["p_mount"] = "地面安装 (Floor)"
                st.session_state["p_persona"] = "聚焦 DIY 个人房主 (极简安装与防呆)"
                st.session_state["p_pkg"] = "热缩膜带展示卡 (Shrink Wrap w/ Header Card) - 经济畅销型"
                st.session_state["p_acc"] = "无螺丝紧固件（免螺丝Drop-in落入式设计），带防震消音海绵缓冲垫"
                st.session_state["p_price"] = "零售目标: $14.99 - $19.99 | 落地成本: <= $4.20"
                st.session_state["p_comp"] = "Decor Grates 4x10 Cast Aluminum; Accord Ventilation 4x10 Register"
                st.session_state["p_focus"] = "1. 重点深挖量错表面尺寸退货\n2. 重点考察细高跟卡死与安全防护\n3. 重点解决踩踏变形与机械松动"
                st.session_state["p_imgs"] = "- [出风口测量与结构部位对照图](https://drive.google.com/file/d/1xZLbD0u2HuxXqasLykMmyg9UjLAE--IV/view?usp=drivesdk)"
                st.rerun()
        with col_t2:
            if st.button("🧹 一键清空输入框"):
                for k in ["p_channel", "p_name", "p_url", "p_size", "p_mat", "p_load", "p_mount", "p_persona", "p_pkg", "p_acc", "p_price", "p_comp", "p_focus", "p_imgs"]:
                    st.session_state[k] = ""
                st.rerun()

    ch_opts = ["The Home Depot (THD)", "Lowe's", "Dual-Channel (THD + Lowe's 跨渠道对标)"]
    def_ch = st.session_state.get("p_channel", ch_opts[0])
    ch_idx = ch_opts.index(def_ch) if def_ch in ch_opts else 0
    channel_mode = st.selectbox("1. 目标零售渠道 :red[* (必选)]", options=ch_opts, index=ch_idx)
    
    project_type = st.selectbox(
        "2. 项目核心类型 :red[* (必选)]",
        options=["竞品差评归因与改良", "新品自主定义开发", "Listing 深度优化", "Buyer 选品提案", "成本结构重构", "规格升级"]
    )
    
    product_name = st.text_input("3. 目标品名 (英文 + 中文) :red[* (必填)]", value=st.session_state.get("p_name", ""), placeholder="例如：Floor Register 或 3/4 in. Half Clamp")
    product_url = st.text_input("4. 目标产品官方链接 / SKU :red[* (必填)]", value=st.session_state.get("p_url", ""), placeholder="例如：The Home Depot / Lowe's 详情页链接或 Store SKU")
    nominal_size = st.text_input("5. 标称开孔/关键尺寸基准 :red[* (必填)]", value=st.session_state.get("p_size", ""), placeholder="例如：4x10 inches、3/4 inch 管径等")
    material_and_finish = st.text_input("6. 预定材质与表面处理 (选填)", value=st.session_state.get("p_mat", ""), placeholder="例如：重型铸铝哑光黑喷粉、304不锈钢、ABS耐冲击塑料")
    load_and_safety = st.text_input("7. 承重/受力与安全规范标准 (选填)", value=st.session_state.get("p_load", ""), placeholder="例如：承重 >= 300 lbs、耐腐蚀无泄漏")
    
    mount_opts = [
        "厨卫/橱柜/台面/管道 (Kitchen, Bath & Plumbing)",
        "地面安装 (Floor)",
        "墙面/天花板安装 (Wall & Ceiling)",
        "门窗/出入口五金 (Doors & Hardware)",
        "户外/甲板/庭院 (Outdoor & Deck)",
        "独立放置/免安装 (Freestanding/Portable)",
        "自定义安装载体"
    ]
    def_mount = st.session_state.get("p_mount", mount_opts[0])
    mount_idx = mount_opts.index(def_mount) if def_mount in mount_opts else 0
    mounting_type = st.selectbox("8.1 产品安装部位 / 应用大类 :red[* (必选)]", options=mount_opts, index=mount_idx)

    substrate_map = {
        "厨卫/橱柜/台面/管道 (Kitchen, Bath & Plumbing)": [
            "PEX/铜管/PVC管", "木龙骨/立柱 (Wood Studs)", "水泥砂浆底座", "瓷砖地面/台面 (Tile)", "木质底板 (Subfloor)", "不锈钢台盆 (Stainless Steel)"
        ],
        "地面安装 (Floor)": [
            "实木地板 (Hardwood)", "锁扣地板 (LVP/SPC)", "瓷砖 (Tile)", "地毯 (Carpet)", "水泥地面 (Concrete)"
        ],
        "墙面/天花板安装 (Wall & Ceiling)": [
            "石膏板 (Drywall/Sheetrock)", "木龙骨 (Wood Studs)", "集成吊顶板 (Drop Ceiling Tile)", "砖石/水泥墙 (Masonry)"
        ],
        "门窗/出入口五金 (Doors & Hardware)": [
            "实木门/门框 (Solid Wood)", "空心木门 (Hollow Core)", "铝合金框 (Aluminum Frame)", "塑钢型材 (Vinyl/PVC)", "钢制安全门 (Steel Door)"
        ],
        "户外/甲板/庭院 (Outdoor & Deck)": [
            "防腐木 (Pressure-Treated Wood)", "塑木复合材料 (Composite Decking)", "水泥混凝土 (Concrete)", "泥土草坪 (Soil/Lawn)"
        ],
        "独立放置/免安装 (Freestanding/Portable)": [
            "平整室内硬质地面", "工作台面 (Workbench)", "置物货架 (Shelving)"
        ],
        "自定义安装载体": [
            "通用硬质基体", "软质基体", "金属外壳"
        ]
    }

    current_options = substrate_map.get(mounting_type, ["通用硬质基体"])
    selected_substrates = st.multiselect(
        "8.2 目标安装介质/接触材质 :red[* (必选)]",
        options=current_options,
        default=current_options[:2] if len(current_options) >= 2 else current_options,
        key=f"sub_{mounting_type}"
    )

    persona_opts = [
        "全客群通用 (DIY房主 + PRO承包商双轮驱动)",
        "聚焦 DIY 个人房主 (极简安装与防呆)",
        "聚焦 PRO 专业施工承包商 (快速作业与耐操耐久)"
    ]
    def_persona = st.session_state.get("p_persona", persona_opts[0])
    p_idx = persona_opts.index(def_persona) if def_persona in persona_opts else 0
    target_persona = st.selectbox("8.3 目标核心客群画像 :red[* (必选)]", options=persona_opts, index=p_idx)

    pkg_opts = [
        "热缩膜带展示卡 (Shrink Wrap w/ Header Card) - 经济畅销型",
        "双面高透吸塑泡壳 (Clamshell Blister Pack) - 防盗抗撕挂钩型",
        "独立开窗瓦楞彩盒 (Corrugated Box w/ Window) - 高端防摔防护型",
        "工程批发大包装 (Contractor Bulk Pack) - 工地大宗出货型"
    ]
    def_pkg = st.session_state.get("p_pkg", pkg_opts[0])
    pkg_idx = pkg_opts.index(def_pkg) if def_pkg in pkg_opts else 0
    packaging_type = st.selectbox("8.4 零售陈列与包装形态 (选填)", options=pkg_opts, index=pkg_idx)

    included_accessories = st.text_input("8.5 随附配件与紧固件策略 (选填)", value=st.session_state.get("p_acc", ""), placeholder="例如：含 2 枚镀锌自攻螺丝；或标明：裸机免螺丝设计")
    target_price = st.text_input("9. 目标零售价与成本线 (USD) (选填)", value=st.session_state.get("p_price", ""), placeholder="例如：零售 $14.99 - $19.99 | 落地成本 <= $4.20")
    competitors = st.text_area("10. 指定竞品对标链接/型号 (选填)", value=st.session_state.get("p_comp", ""), placeholder="若留空，系统将全网自动检索匹配畅销竞品", height=70)
    focus_points = st.text_area("11. 专项排他约束/关注痛点 (选填)", value=st.session_state.get("p_focus", ""), placeholder="例如：重点深挖退货原因、细高跟卡脚、踩踏变形等", height=70)
    image_ref_urls = st.text_area("12. 部位与样品图库链接 (选填)", value=st.session_state.get("p_imgs", ""), placeholder="粘贴产品的 Markdown 图片链接供报告嵌入", height=70)

    st.markdown("---")
    extra_live_data = st.text_area("💡 实时数据补充仓 (选填)", value="", placeholder="可粘贴商品参数卡片、买家评论文本，系统将强制作为事实基准")

# ==============================================================================
# 6. 提示词构建器
# ==============================================================================
def build_prompts():
    context_header = f"""
【SOP V3.0 启动单输入参数】
- 目标渠道: {channel_mode}
- 项目类型: {project_type}
- 当前目标分析产品: 【{product_name}】
- 官方详情页链接 / 编码: {product_url}
- 标称开孔/尺寸基准: {nominal_size}
- 材质与表面处理: {material_and_finish}
- 承重与物理安全/规范: {load_and_safety}
- 安装部位与介质: 【安装部位: {mounting_type} | 介质载体: {', '.join(selected_substrates)}】
- 目标核心买家群体: {target_persona}
- 零售陈列与包装形态: {packaging_type}
- 随附配件与紧固件策略: {included_accessories}
- 目标价格与成本线: {target_price}
- 指定对标竞品: {competitors}
- 核心关注痛点与约束: {focus_points}
- 可调用的产品部位与设计样品图库:
{image_ref_urls}

【隔离与防假信息红线】：
你必须针对具体产品【{product_name}】展开分析！
1. 严禁混淆品类部件；
2. 绝对真实可信：关键价格、评分、SKU、尺寸、认证标准附带可点击 Markdown 超链接 [来源页面](URL)；查不到时标注【未找到公开源】。
"""
    p1 = f"""{context_header}
请严格执行《SOP V3.0》的【Stage 1: 物理架构与规格基准库】（Node 00, 00.5, 01, 02）：
1. 【00 & 00.5 项目章程与渠道界定】：用大白话明确在 {channel_mode} 渠道下的业务目标与准入审核标准。
2. 【01 产品基础规格拆解库】：
   - 提取最新参数（价格、评分、SKU/Item编号、质保、官方认证标准如 ASTM / cUPC / ADA / IBC 等）。
   - 【尺寸大白话解耦 + 实体英文双语】：彻底区分开孔标称、配合部与表面外沿尺寸，讲清量哪里才不会买错退货。
   - 建立结构化【Product Specification Database】双语表格（公制mm与英制对照）。
3. 【02 渠道产品定位】：分析在 {channel_mode} 货架上的生态位与用户购买动机。
格式统一使用：【中文通俗名 (北美行业地道英文 Native Term)】。
"""
    p2 = f"""{context_header}
请严格执行《SOP V3.0》的【Stage 2: 场景矩阵、适配性与真实 VOC 挖掘】（Node 03, 04, 05, 05.5）：
1. 【03 真实四维场景矩阵】：结合所选【安装部位: {mounting_type}】与【介质: {', '.join(selected_substrates)}】，用大白话讲清当前产品【{product_name}】在日常使用中的受力与工况。
2. 【04 适配性与安装干涉】：针对不同介质，讲透会不会松动、脱落或损坏载体。
3. 【05 真实买家 VOC 深度挖掘】：引用该产品真实 1~5 星英文差评原声词并附带中文翻译，标注痛点根源。
4. 【05.5 竞品 VOC 对标分析】：对比参考竞品，讲清行业通病与当前款特有缺陷。
"""
    p3 = f"""{context_header}
请严格执行《SOP V3.0》的【Stage 3: 根因归因、结构拆解与制造工艺】（Node 06, 07, 07.5）：
1. 【06 差评根因归因链 (Root Cause)】：建立链条：买家抱怨 → 物理破坏表象 → 核心机械/材质失效根因。
2. 【07 物理结构拆解 (Teardown)】：针对当前产品【{product_name}】拆解核心零配件，使用地道英文双语标明。
3. 【07.5 制造工艺与质量风险】：通俗讲解材质加工（注塑、冲压、压铸、粉末喷涂等）常见的缩水、开裂、生锈及公差失效风险。
"""
    p4 = f"""{context_header}
请严格执行《SOP V3.0》的【Stage 4: 商业数据库、机会排序与下一代产品定义】（Node 08, 09, 09.5, 10, 11, 11.5, 12, 13, 14）：
1. 【08-09 竞品横评数据库】：多竞品横向比对表（最新价格、评分、卖点与缺陷）。
2. 【09.5 成本结构测算】：估算 BOM 材料、模具分摊、包装与海运落地成本 (Landed Cost)。
3. 【11-12 痛点排序与设计机会】：建立 `VOC 痛点 → 根因 → 机会 → 结构改良` 闭环。
4. 【13-14 下一代产品定义】：明确硬指标 (Must-Have P0) 与体验升级 (Should-Have P1)。
"""
    p5 = f"""{context_header}
请严格执行《SOP V3.0》的【Stage 5: 验证计划、渠道专属 Listing 与 20 问终极闭环】（Node 15, 16, 17, 18）：
1. 【15 EVT / DVT / PVT 工程测试计划】：受力测试、跌落测试与耐候腐蚀测试标准（引用 ASTM / IBC 官方标准全称）。
2. 【16 {channel_mode} 专属 Listing 策略】：
   - 【高转化英文 Title】：符合北美搜索算法的高转化商品标题。
   - 【Native English Bullet Points】：地道 5 点卖点（英文原生文案 + 中文对照）。
   - 【小白防买错指南 (Compatibility Guide)】：用大白话教买家测量选型，阻断退货。
3. 【17 终版产品工程规格卡片】：核心量产参数清单。
4. 【18 终极闭环：解答 20 个产品开发核心决策问题】。
"""
    p6_base = f"""{context_header}
请执行 SOP 的【压轴 Stage 6: 汇报级终极决策总结看板 (Executive Summary Dashboard)】：
文字必须采用通俗大白话，关键部件采用【中文通俗名 (北美行业地道英文 Native Term)】双语标注。
请严格按照以下四大模块精炼输出一页纸汇报看板：
1. 🚦【致命缺陷红绿灯诊断表 (Fatal Flaws Red/Yellow/Green)】：
   - 提取导致退货差评的 Top 致命痛点（🔴 极高风险 / 🟡 中高风险 / 🟢 优化项）。
   - 列出：受损部位、买家原声、通俗工程改进措施、检验标准。
2. 📊【核心硬性工程红线指标速查表 (Critical Specs Baseline)】：
   - 提取物理与工程硬指标（含公制/英制双轨数值与公差）。
3. 🏆【产品选型与渠道落地决策 (Product Selection & GTM)】：
   - 推荐方案的定位、差异化优势与渠道定价。
4. 📋【下一步立即可执行行动清单 (Action Items)】：
   - 打样验证、包装防退货整改、首单采购建议。
"""
    return [p1, p2, p3, p4, p5, p6_base]

# ==============================================================================
# 7. 执行控制栏与流水线
# ==============================================================================
col_btn, col_clear, col_info = st.columns(3)
with col_btn:
    run_all_btn = st.button("🚀 启动 SOP V3.0 全流程分析 (实时准确模式)", type="primary", use_container_width=True)
with col_clear:
    if st.button("🧹 清空当前数据 (换新产品)", use_container_width=True):
        for i in range(1, 7):
            st.session_state[f"stage{i}_res"] = ""
        st.session_state["analyzed_product_name"] = ""
        st.success("已清空历史数据！")
        st.rerun()
with col_info:
    if not api_key:
        st.info(f"💡 请先在左侧填入 {provider.split(' ')[0]} API Key 即可启动。")

if run_all_btn:
    if not api_key:
        st.error(f"启动失败：缺少 {provider.split(' ')[0]} API Key，请在左侧侧边栏填入。")
    elif not product_name.strip() or not nominal_size.strip() or not product_url.strip():
        st.error("启动失败：请填写所有标红【* (必填)】项（目标品名、尺寸基准、产品链接）。")
    else:
        for i in range(1, 7):
            st.session_state[f"stage{i}_res"] = ""
        st.session_state["analyzed_product_name"] = product_name
        
        prompts = build_prompts()
        stage_names = [
            "Stage 1 物理架构与规格库 (通俗白话+部位图)",
            "Stage 2 场景适配与 VOC 挖掘 (生活大白话)",
            "Stage 3 根因归因与结构制造 (图文拆解)",
            "Stage 4 机会矩阵与下一代定义 (样品对比)",
            "Stage 5 验证计划与 Listing (防买错指南)",
            "Stage 6 汇报级终极决策总结看板 (一页纸决策)"
        ]
        search_queries = [
            f"{product_name} Home Depot price specifications dimensions review",
            f"{product_name} reviews complaints problems leakage fail",
            f"{product_name} teardown broken cracked failure internal structure",
            f"{competitors} price rating comparison" if competitors.strip() else f"{product_name} top competitors",
            f"{product_name} installation manual test standard",
            f"{product_name} executive summary decision benchmark"
        ]
        
        progress_bar = st.progress(0, text="🚀 正在启动全流程流水线...")
        has_failed = False
        
        for idx in range(6):
            stage_idx = idx + 1
            accumulated_memory = get_accumulated_context(stage_idx)
            current_stage_prompt = prompts[idx] + accumulated_memory
            
            progress_bar.progress(idx / 6, text=f"正在分析第 {stage_idx}/6 阶段: {stage_names[idx]}...")
            
            res = execute_stage(
                provider, api_key, model_name, current_stage_prompt, stage_names[idx], 
                search_query=search_queries[idx], base_url_val=custom_base_url,
                temp_val=temperature, extra_data=extra_live_data
            )
            st.session_state[f"stage{stage_idx}_res"] = res

            if idx == 0 and res.startswith("❌"):
                has_failed = True
                st.error("第一阶段调用异常（API Key 或模型不可用），已自动熔断。")
                break
                
            if idx < 5:
                time.sleep(1.5)
                
        if not has_failed:
            progress_bar.progress(1.0, text="✅ 全部 6 个阶段分析圆满完成！")
            save_project_to_disk(product_name, channel_mode)
            st.success(f"🎉 【{product_name}】分析报告已生成并自动保存至本地记录库！")

# ==============================================================================
# 8. 成果展示与报告导出
# ==============================================================================
if any(st.session_state[f"stage{i}_res"] for i in range(1, 7)):
    tab_sum, tab1, tab2, tab3, tab4, tab5, tab_full = st.tabs([
        "📊 Stage 6: 汇报级总结看板",
        "📐 Stage 1: 规格基准库",
        "🏡 Stage 2: 场景与真实 VOC",
        "🔬 Stage 3: 根因与结构拆解",
        "💡 Stage 4: 机会与下一代定义",
        "🎯 Stage 5: 验证计划与 Listing",
        "📄 完整报告总览与导出"
    ])
    
    prompts = build_prompts()
    
    def render_stage_tab(tab, stage_idx, stage_title, sq):
        with tab:
            render_safe_markdown(st.session_state[f"stage{stage_idx}_res"])
            st.markdown("---")
            if st.button(f"🔄 重新检索并单步重跑 ({stage_title})", key=f"retry_{stage_idx}"):
                accumulated_memory = get_accumulated_context(stage_idx)
                cur_p = prompts[stage_idx-1] + accumulated_memory
                st.session_state[f"stage{stage_idx}_res"] = execute_stage(
                    provider, api_key, model_name, cur_p, stage_title, 
                    search_query=sq, base_url_val=custom_base_url,
                    temp_val=temperature, extra_data=extra_live_data
                )
                save_project_to_disk(product_name, channel_mode)
                st.rerun()

    render_stage_tab(tab_sum, 6, "Stage 6 总结看板", f"{product_name} executive summary report")
    render_stage_tab(tab1, 1, "Stage 1 规格基准库", f"{product_name} Home Depot price specifications")
    render_stage_tab(tab2, 2, "Stage 2 场景与 VOC", f"{product_name} complaints problems review")
    render_stage_tab(tab3, 3, "Stage 3 根因结构拆解", f"{product_name} teardown broken failure")
    render_stage_tab(tab4, 4, "Stage 4 机会与定义", f"{competitors} specs price" if competitors.strip() else f"{product_name} specs")
    render_stage_tab(tab5, 5, "Stage 5 验证与 Listing", f"{product_name} installation manual test")

    with tab_full:
        full_markdown = f"""# {product_name} - 北美大零售产品开发深度调研报告 (SOP V3.0)
- **目标渠道**: {channel_mode} | **驱动引擎**: {provider} ({model_name}) | **生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **标称开孔尺寸**: {nominal_size} | **安装部位与介质**: {mounting_type} - {', '.join(selected_substrates)}

---
# 📊 【高管汇报级一页纸决策看板 (Executive Summary Dashboard)】
{st.session_state.stage6_res}

---
# 📚 深度调研详版报告
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
        render_safe_markdown(full_markdown)
        
        cleaned_size = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', nominal_size.replace('/', '-').replace('"', 'in'))
        safe_base_name = f"{channel_mode.split(' ')[0]}_SOP_V3_{cleaned_size}"
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 下载完整研报 Markdown (.md)",
                data=full_markdown,
                file_name=f"{safe_base_name}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_dl2:
            html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{product_name} - SOP V3.0 深度调研报告</title>
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; padding: 40px; color: #1E293B; max-width: 1000px; margin: 0 auto; }}
    h1 {{ color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; }}
    h2 {{ color: #1E3A8A; margin-top: 24px; border-bottom: 1px solid #CBD5E1; padding-bottom: 6px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
    th, td {{ border: 1px solid #CBD5E1; padding: 10px; text-align: left; }}
    th {{ background-color: #F1F5F9; }}
    pre, code {{ background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 4px; padding: 2px 6px; font-family: monospace; }}
</style>
</head>
<body>
<div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; padding: 16px; border-radius: 8px; margin-bottom: 24px;">
    <h3 style="margin-top:0;">📋 项目基本信息</h3>
    <p><b>产品名称:</b> {product_name} | <b>目标渠道:</b> {channel_mode} | <b>标称尺寸:</b> {nominal_size}</p>
    <p><b>生成日期:</b> {time.strftime('%Y-%m-%d %H:%M:%S')} (在浏览器按 Ctrl+P 可直接存为高清 PDF)</p>
</div>
<pre style="white-space: pre-wrap; font-family: inherit;">
{full_markdown}
</pre>
</body>
</html>"""
            st.download_button(
                label="🖨️ 下载高管汇报排版 HTML / 打印 PDF (.html)",
                data=html_doc,
                file_name=f"{safe_base_name}.html",
                mime="text/html",
                use_container_width=True
            )
