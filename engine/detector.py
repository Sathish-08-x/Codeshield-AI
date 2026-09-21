import re
import math
from typing import Dict, List, Any, Tuple

LANG_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".rb": "ruby",
    ".html": "html",
    ".css": "css",
    ".sql": "sql",
    ".sh": "bash",
    ".json": "json"
}

AI_COMMENT_PATTERNS = [
    (r"(?i)#\s*step\s*\d+[:\s]", "Step-by-step tutorial marker (e.g. '# Step 1:')", 22),
    (r"(?i)//\s*step\s*\d+[:\s]", "Step-by-step tutorial marker (e.g. '// Step 1:')", 22),
    (r"(?i)<!--\s*(?:step\s*\d+|header|navigation|navbar|hero|footer|main\s+content|section|cards?|container|sidebar|start|end).*?-->", "AI HTML Section Divider Comment", 26),
    (r"(?i)<!--\s*(?!TODO|FIXME|NOTE|BUG|TEMP|HACK).*?(?:Section|Divider|Component|Layout|Start|End|wrapper|container|content)\s*-->", "AI HTML Generic Divider Comment", 16),
    (r"(?i)#\s*helper\s+function\s+to", "Generic helper function commentary", 18),
    (r"(?i)//\s*helper\s+function\s+to", "Generic helper function commentary", 18),
    (r"(?i)(#|//)\s*(example\s+usage|usage\s+example|test\s+cases?)\b", "AI boilerplate usage/test example header", 22),
    (r"(?i)(#|//)\s*initialize\s+(the\s+)?(variables?|data|list|array|dictionary|state)", "Trivial AI initialization comment", 16),
    (r"(?i)(#|//)\s*define\s+(the\s+)?(function|class|method|schema|route|model)", "Redundant definition comment", 15),
    (r"(?i)(#|//)\s*handle\s+(the\s+)?(error|exception|case|event)", "Generic error-handling comment", 14),
    (r"(?i)(#|//)\s*check\s+if\s+(the\s+)?[a-z_0-9]+\s+is\s+valid", "Generic validation comment", 15),
    (r"(?i)(#|//)\s*print\s+(the\s+)?(result|output|response)", "Trivial print output comment", 14),
    (r"(?i)(#|//)\s*create\s+an\s+instance\s+of", "Textbook instantiation comment", 14),
    (r"(?i)(#|//)\s*loop\s+through\s+(each\s+|the\s+)", "Trivial loop explanation", 16),
    (r"(?i)(#|//)\s*return\s+(the\s+)?(result|response|value|sum|boolean|true|false)", "Trivial return statement comment", 15),
    (r"(?i)(#|//)\s*here\s+(we|is\s+where\s+we)\b", "Conversational AI tutorial phrasing ('Here we...')", 24),
    (r"(?i)(#|//)\s*note:\s*(you\s+can|this\s+is\s+a\s+simplified|in\s+production)", "Conversational AI disclaimer note", 24),
    (r"(?i)(#|//)\s*(base\s+case|recursive\s+case|recursive\s+step)\b", "Textbook algorithmic comment", 18),
    (r"(?i)(#|//)\s*(time\s+complexity|space\s+complexity|o\([n1log\s]+\))\b", "Pedagogical complexity remark", 20),
    (r"^```[a-z]*\s*$", "Markdown code fence artifact left in file", 35),
]

AI_NAMING_PATTERNS = [
    r"\b(user_input|user_data|data_list|item_list|result_list|temp_list|final_result|current_item|total_sum|total_score)\b",
    r"\b(grade_records|student_item|valid_count|passed_students|average_score|score_records|record_list|item_count)\b",
    r"\b(sanitizedUserList|sanitized_user_list|currentIterationIndex|current_iteration_index|temporaryBufferData|temp_buffer_data)\b",
    r"\b(isUserCurrentlyActive|is_user_currently_active|calculatedTotalDiscountAmount|calculated_total_discount_amount)\b",
    r"\b(calculate_total\w*|process_data\w*|process_student\w*|handle_request\w*|fetch_user\w*|validate_input\w*)\b",
    r"\b(dummy_data|sample_data|mock_data|test_input|input_values|test_cases)\b",
    r"\b(is_valid|has_error|success_flag|status_code_ok|is_palindrome|cleaned_text|cleaned_str|cleaned)\b",
    r"\b(char_count|word_count|filtered_words|target_sum|current_sum|num_list|string_val)\b",
    r"\b(nav-links|hero-section|feature-card|features-container|cta-button|logo-text|footer-links)\b"
]

AI_SYNTAX_PATTERNS = [
    (r"(?i)<!DOCTYPE\s+html>\s*<html\s+lang=[\"']en[\"']>\s*<head>\s*<meta\s+charset=[\"']UTF-8[\"']>", "Sterile AI boilerplate HTML5 skeleton", 30),
    (r"(?i)<header\s+class=[\"']navbar[\"']>\s*<div\s+class=[\"']logo[\"']>[^<]*<span>[^<]*</span></div>\s*<nav>\s*<ul\s+class=[\"']nav-links[\"']>", "Stereotypical AI navbar/landing page layout", 32),
    (r"def\s+[a-zA-Z_0-9]+\s*\([^)]*?:\s*(?:str|int|float|bool|list|dict|List|Dict|Tuple|Optional|Any)[^)]*?\)\s*->\s*(?:str|int|float|bool|list|dict|List|Dict|Tuple|Optional|Any|None)", "Rigid AI type-annotated function signature", 28),
    (r'(?:""|"\s*")\.join\(\s*[a-zA-Z_0-9]+\s+for\s+[a-zA-Z_0-9]+\s+in\s+[^)]*?\)', "Chained generator expression inside string join", 25),
    (r"\[\s*[a-zA-Z_0-9]+\s*(?:\.[a-zA-Z_0-9]+\(\))?\s+for\s+[a-zA-Z_0-9]+\s+in\s+[^\]]+?\]", "Concise list comprehension pipeline", 22),
    (r"\[::-1\]", "Pythonic slice reversal shorthand", 20),
    (r"\b(?:isalnum|isalpha|isdigit)\(\)", "Textbook string classification method", 15),
    (r"(?s)[\'\"]{3}[\s\S]*?[\'\"]{3}", "Textbook docstring block", 22),
    (r"\b(?:sum|any|all)\(\s*(?:\[|\()\s*[a-zA-Z_0-9]+.*?for\s+[a-zA-Z_0-9]+\s+in", "Functional built-in with generator/comprehension", 24),
    (r"\b(?:lambda\s+[a-zA-Z_0-9,\s]+:)", "Lambda function expression", 18),
    (r"(?:\w+\s+if\s+.*?\s+else\s+\w+)", "Ternary conditional expression", 18),
    (r"const\s+[a-zA-Z_0-9]+\s*=\s*\([^)]*\)\s*=>", "Modern ES6 arrow function declaration", 20),
    (r"\.(?:map|filter|reduce)\s*\(", "Chained functional array method", 20),
    (r"\bstd::make_unique<|\bstd::unique_ptr<|\bstd::shared_ptr<", "Modern C++ smart pointer safety construct", 25),
]

UNIVERSAL_NORMALIZER_MATRIX = [
    {
        "signature": "Numbered comments (# 1, # 2)",
        "target_models": "OpenAI (GPT-4o, o1, o3-mini)",
        "quirk_description": "Chain-of-thought fine-tuning causes routine step-by-step numbering (# 1. Initialize, # 2. Filter).",
        "normalization_action": "Strip completely via deterministic regex pre-cleaning pass.",
        "icon": "🔢"
    },
    {
        "signature": "'Example Usage' & Demo Harnesses",
        "target_models": "Anthropic Claude, OpenAI",
        "quirk_description": "Appends formatted test runs (// ================= Example Usage =================) and runnable demo blocks.",
        "normalization_action": "Strip trailing example blocks and if __name__ == '__main__': harnesses.",
        "icon": "🧪"
    },
    {
        "signature": "Standard Library Over-Explanation",
        "target_models": "Google Gemini",
        "quirk_description": "Comments explaining what standard libraries do under the hood (e.g. # requests.get automatically follows redirects).",
        "normalization_action": "Strip self-evident stdlib commentary and conversational AI remarks.",
        "icon": "📚"
    },
    {
        "signature": "Terse Algorithm Shorthand (dp, ans, vis)",
        "target_models": "DeepSeek (V3, R1)",
        "quirk_description": "Competitive programming abbreviations (dp, vis, adj, cnt, q) and fast I/O tricks.",
        "normalization_action": "Rename to semantic production variables (cache, visited, graph, count, result).",
        "icon": "⚡"
    },
    {
        "signature": "Over-Modular Auxiliary Helpers",
        "target_models": "OpenAI o1/o3-mini, Claude",
        "quirk_description": "Splits simple logic into 3-4 auxiliary private helpers (_validate_input(), _calculate_helper()).",
        "normalization_action": "Inline trivial single-statement helpers back into the main function context.",
        "icon": "🧩"
    },
    {
        "signature": "Redundant Typing Imports",
        "target_models": "OpenAI, Claude",
        "quirk_description": "Heavy 'from typing import List, Dict, Optional, Any, Union' boilerplate instead of modern native types.",
        "normalization_action": "Simplify to modern Python native builtins (list[str], dict | None).",
        "icon": "🏷️"
    },
    {
        "signature": "Generic Try-Catch with Formatted Prints",
        "target_models": "Google Gemini, OpenAI",
        "quirk_description": "Defensive try-except blocks that merely print f'Error loading config: {e}' and return None.",
        "normalization_action": "Clean error boundaries, replace with domain-specific handling or clean returns.",
        "icon": "🛡️"
    }
]

def detect_ai_model_family(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Diagnoses which major AI family (OpenAI, Anthropic Claude, Google Gemini,
    DeepSeek, or Meta Llama / GitHub Copilot) likely generated the input code
    based on distinct behavioral fingerprints, commenting habits, and syntactic templates.
    """
    if not code or not code.strip():
        return {
            "family_id": "unknown",
            "family": "Unknown",
            "confidence": 0,
            "icon": "❓",
            "badge_class": "badge-neutral",
            "detected_quirks": [],
            "all_scores": {}
        }

    scores = {
        "openai": 0,
        "claude": 0,
        "gemini": 0,
        "deepseek": 0,
        "llama_copilot": 0
    }
    quirks = {
        "openai": [],
        "claude": [],
        "gemini": [],
        "deepseek": [],
        "llama_copilot": []
    }

    numbered_steps = re.findall(r"(?m)^\s*(?:#|//)\s*(?:Step\s*)?\d+[\.:\)]\s*.*$", code)
    if len(numbered_steps) >= 2:
        scores["openai"] += 35 + min(30, len(numbered_steps) * 10)
        quirks["openai"].append(f"Numbered step-by-step comments ({len(numbered_steps)} steps detected)")
    elif len(numbered_steps) == 1:
        scores["openai"] += 15
        quirks["openai"].append("Numbered step comment marker")

    if re.search(r"from\s+typing\s+import\s+.*?(?:List|Dict|Optional|Union|Tuple|Any)", code):
        scores["openai"] += 20
        scores["claude"] += 10
        quirks["openai"].append("Over-specified typing import boilerplate (from typing import List, Dict...)")

    if re.search(r'if\s+__name__\s*==\s*[\x27\x22]__main__[\x27\x22]\s*:', code):
        scores["openai"] += 20
        scores["gemini"] += 10
        quirks["openai"].append("Boilerplate entry-point test scaffold (if __name__ == '__main__':)")

    private_helpers = re.findall(r"def\s+_[a-zA-Z0-9_]+\s*\(", code)
    if len(private_helpers) >= 2:
        scores["openai"] += 25
        quirks["openai"].append(f"Reasoning model auxiliary helper sprawl ({len(private_helpers)} private micro-functions)")

    if re.search(r"(?i)(?://\s*=*|/\*)\s*example\s+usage", code) or re.search(r"(?i)//\s*={5,}\s*\n//\s*Example Usage", code):
        scores["claude"] += 45
        quirks["claude"].append("Architectural 'Example Usage' footer test harness")

    algo_headings = re.findall(r"(?i)//\s*(?:uses|utilizes|implements)\s+.*?(?:technique|algorithm|o\(n\)|two-pointer|sliding\s+window)", code)
    if algo_headings:
        scores["claude"] += 35
        quirks["claude"].append("Pedagogical algorithmic heading comment (e.g. '// Uses two-pointer technique')")

    func_chains = re.findall(r"\.(?:reduce|filter|map)\s*\(", code)
    if len(func_chains) >= 2:
        scores["claude"] += 20
        quirks["claude"].append(f"High density functional pipeline ({len(func_chains)} chained array operations)")

    if re.search(r"/\*\*[\s\S]*?@param[\s\S]*?\*/", code) or re.search(r"type\s+\w+\s*=\s*\{\s*status:", code):
        scores["claude"] += 20
        quirks["claude"].append("Rigid JSDoc or discriminated union type structure")

    stdlib_explain = re.search(r"(?i)#\s*.*?(?:automatically\s+follows|decodes\s+gzip|built-in\s+method|under\s+the\s+hood|automatically\s+handles)", code)
    if stdlib_explain:
        scores["gemini"] += 40
        quirks["gemini"].append("Standard library pedagogical over-explanation comment")

    formatted_err_print = re.search(r"(?s)except\s+\w+\s+as\s+e:\s*\n\s*print\(f?[\x27\x22](?:Error|Failed).*?\{e\}", code)
    if formatted_err_print:
        scores["gemini"] += 35
        quirks["gemini"].append("Formatted exception printing pattern (print(f'Error: {e}'))")

    env_leakage = re.search(r"(?i)(#|//)\s*(?:replace\s+with\s+your|make\s+sure\s+to\s+install|install\s+via\s+pip|here\s+is\s+the\s+complete)", code)
    if env_leakage:
        scores["gemini"] += 25
        scores["openai"] += 15
        quirks["gemini"].append("Self-contained environment setup / conversational AI leakage")

    dp_vars = set(re.findall(r"\b(ans|res|dp|vis|adj|cnt|q)\b", code))
    if len(dp_vars) >= 2:
        scores["deepseek"] += 30 + (len(dp_vars) * 12)
        quirks["deepseek"].append(f"Competitive programming / LeetCode variable tropes: {', '.join(sorted(dp_vars))}")

    if re.search(r"(?:sys\.stdin\.readline|sync_with_stdio\s*\(\s*false|cin\.tie)", code):
        scores["deepseek"] += 40
        quirks["deepseek"].append("Algorithmic fast I/O optimization (sys.stdin.readline / sync_with_stdio)")

    if re.search(r"(?i)(?:dp\[i\]\[j\]\s*=|recurrence\s+relation|binary\s+lifting|fenwick|segment\s+tree)", code):
        scores["deepseek"] += 35
        quirks["deepseek"].append("DeepSeek-R1 optimal mathematical algorithm structure")

    if re.search(r"(?s)if\s+(\w+)\s+is\s+not\s+None:\s*\n\s*if\s+\1:", code):
        scores["llama_copilot"] += 30
        quirks["llama_copilot"].append("Repetitive / redundant nested null-checks")

    lines = [l.strip() for l in code.splitlines() if l.strip() and not l.strip().startswith(("#", "//"))]
    dups = len(lines) - len(set(lines))
    if dups >= 3 and len(lines) > 6:
        scores["llama_copilot"] += 20
        quirks["llama_copilot"].append("Autocomplete line repetition artifacts")

    max_family = max(scores, key=scores.get)
    max_score = scores[max_family]

    family_meta = {
        "openai": {
            "name": "OpenAI (GPT-4o / o1)",
            "icon": "🤖",
            "badge_class": "badge-openai",
            "default_quirk": "Step-by-step explanatory comments & runnable mock scaffolds."
        },
        "claude": {
            "name": "Anthropic Claude (3.5 Sonnet)",
            "icon": "🎭",
            "badge_class": "badge-claude",
            "default_quirk": "Architectural cleanliness, functional pipelines & Example Usage headers."
        },
        "gemini": {
            "name": "Google Gemini (1.5 / 2.0)",
            "icon": "✨",
            "badge_class": "badge-gemini",
            "default_quirk": "Standard library over-explanations & formatted exception printing."
        },
        "deepseek": {
            "name": "DeepSeek (V3 / R1)",
            "icon": "⚡",
            "badge_class": "badge-deepseek",
            "default_quirk": "Competitive programming abbreviations (dp, ans, vis) & mathematical algorithms."
        },
        "llama_copilot": {
            "name": "Meta Llama 3 / GitHub Copilot",
            "icon": "🦙",
            "badge_class": "badge-copilot",
            "default_quirk": "Autocomplete repetitions & redundant defensive checks."
        }
    }

    if max_score >= 20:
        meta = family_meta[max_family]
        confidence = min(98, max(42, int(max_score * 1.15)))
        detected_family = meta["name"]
        icon = meta["icon"]
        badge = meta["badge_class"]
        found_quirks = quirks[max_family] or [meta["default_quirk"]]
    else:
        detected_family = "Generic / Hybrid LLM"
        confidence = 35
        icon = "⚙️"
        badge = "badge-generic"
        found_quirks = ["Standard LLM statistical predictability across multiple model signatures."]

    return {
        "family_id": max_family if max_score >= 20 else "generic",
        "family": detected_family,
        "name": detected_family,
        "confidence": confidence,
        "icon": icon,
        "badge_class": badge,
        "detected_quirks": found_quirks,
        "quirks": found_quirks,
        "all_scores": scores
    }

AI_PROCEDURAL_PATTERNS = [
    (r"(?m)^\s*([a-zA-Z_0-9]+)\s*=\s*0\s*\n\s*([a-zA-Z_0-9]+)\s*=\s*0\s*\n\s*([a-zA-Z_0-9]+)\s*=\s*\[\]", "Procedural accumulator setup (total=0, count=0, list=[])", 22),
    (r"\.get\([\'\"][a-zA-Z_0-9]+[\'\"]\)\s+is\s+not\s+None", "Over-defensive `.get() is not None` edge-case check", 18),
    (r"[a-zA-Z_0-9]+\s*/\s*[a-zA-Z_0-9]+\s+if\s+[a-zA-Z_0-9]+\s*>\s*0\s+else\s+0", "Stereotypical guarded ternary division (`total / count if count > 0 else 0`)", 16),
    (r"for\s+[a-zA-Z_0-9]+_item\s+in\s+[a-zA-Z_0-9]+_records:", "Hyper-formal loop iteration variable naming", 18),
    (r"(?s)if\s+(?:re\.(?:match|search)|[a-zA-Z_0-9]+)\([^)]*\)\s*:\s*\n\s*return\s+True\s*\n\s*return\s+False", "Verbose boolean if-return-True ladder (lack of idiomatic bool() return)", 18),
]

AI_ARCHETYPE_PATTERNS = [
    (r'(?m)^\s*if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', "Self-contained entry point wrapper (`if __name__ == '__main__':`)", 18),
    (r'\b(sample_data|mock_data|test_input|test_array|dummy_list|example_input|input_list)\s*=\s*\[', "Mock data array populated with tidy sample inputs", 20),
    (r'\brecords\s*=\s*\[\s*\{\s*[\'\"]name[\'\"]\s*:\s*[\'\"]Alice[\'\"]', "Tidy mock test dataset with sample student names (Alice, Bob, Charlie)", 22),
    (r'(?i)print\s*\(\s*f?["\'](result|output|total\s*sum|the\s*sum\s*is|final\s*result|calculated)\s*[:=]', "Neatly formatted result print statement", 16),
    (r'"""[\s\S]*?Args:[\s\S]*?Returns:[\s\S]*?"""', "Rigid textbook Google/Sphinx docstring template", 15),
    (r'(?i)(#|//)\s*(example\s+usage|usage\s+example|test\s+cases?)\b', "Helpful assistant example usage header", 16)
]

def detect_language(filename: str, code: str) -> str:
    if filename and filename != "snippet.py" and "." in filename:
        for ext, lang in LANG_EXTENSIONS.items():
            if filename.lower().endswith(ext):
                return lang

    if re.search(r"(?i)<!DOCTYPE\s+html|<html[\s>]|<head[\s>]|<body[\s>]|<div[\s>]|<header[\s>]", code):
        return "html"
    if re.search(r"(?i)\b(?:select\s+.*?\s+from|insert\s+into|create\s+table|update\s+\w+\s+set)\b", code):
        return "sql"
    if re.search(r"#include\s*<[a-z]+>|std::", code):
        return "cpp"
    if re.search(r"public\s+class\s+[a-zA-Z_0-9]+|System\.out\.println", code):
        return "java"
    if re.search(r"def\s+[a-zA-Z_0-9]+\s*\(.*?\):|import\s+[a-zA-Z_]+", code):
        return "python"
    if re.search(r"(?:\bfunction\s+[a-zA-Z_0-9]+\s*\(|\bconst\s+[a-zA-Z_0-9]+\s*=|console\.(?:log|error|warn)|\bawait\s+fetch\b|\bnew\s+FileReader\b|\bdocument\.(?:getElementById|querySelector))", code):
        return "javascript"
    if re.search(r"(?m)^\s*(?!(?:try|catch|finally|if|else|while|for|switch|case|function|class|interface|struct|enum|return)\b)[.#]?[a-zA-Z_0-9-]+\s*\{[^}]*?(?:color|background|font|margin|padding|display|border|width|height)\s*:", code) or re.search(r"@media|@keyframes|:root\s*\{", code):
        return "css"
    if re.search(r"package\s+main|func\s+[a-zA-Z_0-9]+", code):
        return "go"
    if re.search(r"fn\s+main\s*\(|let\s+mut\s+", code):
        return "rust"
    return "plaintext"

def analyze_entropy_and_regularity(lines: List[str]) -> Tuple[float, Dict[str, Any]]:
    """Measures the uniformity and predictability of line lengths and indentations."""
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return 0.0, {"line_uniformity": 0.0, "indent_regularity": 0.0}

    lengths = [len(l.rstrip()) for l in non_empty]
    mean_len = sum(lengths) / len(lengths)
    var_len = sum((x - mean_len) ** 2 for x in lengths) / len(lengths)
    std_len = math.sqrt(var_len)

    uniformity_score = 0.0
    if 8.0 <= std_len <= 26.0 and len(lengths) > 8:
        uniformity_score = max(0.0, 1.0 - abs(std_len - 17.0) / 15.0) * 18.0

    indents = [len(l) - len(l.lstrip()) for l in non_empty]
    indent_steps = [indents[i] - indents[i-1] for i in range(1, len(indents))]
    regular_steps = [s for s in indent_steps if s in (0, 2, 4, -2, -4)]
    indent_ratio = len(regular_steps) / len(indent_steps) if indent_steps else 1.0
    indent_score = (indent_ratio * 12.0) if indent_ratio > 0.85 else 0.0

    return uniformity_score + indent_score, {
        "mean_line_length": round(mean_len, 1),
        "std_line_length": round(std_len, 1),
        "uniformity_contribution": round(uniformity_score, 1),
        "indent_regularity_ratio": round(indent_ratio, 2)
    }

def analyze_burstiness(lines: List[str]) -> Tuple[float, float]:
    """
    Human code is bursty: high token variation window to window.
    AI code is smooth and uniform across windows.
    """
    tokens_per_line = [len(re.findall(r"\w+", l)) for l in lines if l.strip()]
    if len(tokens_per_line) < 6:
        return 0.0, 0.0

    window_size = 3
    window_sums = []
    for i in range(0, len(tokens_per_line) - window_size + 1):
        window_sums.append(sum(tokens_per_line[i:i+window_size]))

    if not window_sums:
        return 0.0, 0.0

    mean_win = sum(window_sums) / len(window_sums)
    var_win = sum((w - mean_win) ** 2 for w in window_sums) / len(window_sums)
    std_win = math.sqrt(var_win)

    cv = (std_win / mean_win) if mean_win > 0 else 0.0

    ai_burst_score = 0.0
    if cv < 0.35 and len(tokens_per_line) > 10:
        ai_burst_score = (0.35 - cv) / 0.35 * 18.0

    return round(ai_burst_score, 1), round(cv, 3)

def detect_ai_code(code: str, filename: str = "snippet.py") -> Dict[str, Any]:
    """
    Analyzes code string and returns comprehensive AI score, indicators,
    metrics breakdown, and per-line heatmap.
    """
    if not code or not code.strip():
        return {
            "ai_score": 0.0,
            "verdict": "Empty",
            "language": "plaintext",
            "indicators": [],
            "metrics": {},
            "line_heatmaps": []
        }

    language = detect_language(filename, code)
    lines = code.splitlines()
    total_lines = len(lines)
    non_blank_lines = [l for l in lines if l.strip()]

    indicators = []
    line_scores = [0.0] * total_lines
    line_reasons = [""] * total_lines

    comment_pattern_hits = 0
    comment_weight_total = 0.0
    total_comment_lines = 0

    for idx, line in enumerate(lines):
        clean_l = line.strip()
        is_comment = clean_l.startswith(("#", "//", "/*", "*", '"""', "'''"))
        if is_comment:
            total_comment_lines += 1

        for pat, desc, weight in AI_COMMENT_PATTERNS:
            if re.search(pat, line):
                comment_pattern_hits += 1
                comment_weight_total += weight
                line_scores[idx] = max(line_scores[idx], min(95.0, weight * 4.0))
                line_reasons[idx] = desc
                indicators.append({
                    "name": "AI Commentary Signature",
                    "severity": "high" if weight >= 18 else "medium",
                    "description": f"Found '{desc}' on line {idx + 1}",
                    "line": idx + 1,
                    "code_snippet": clean_l[:80]
                })
                break

    comment_ratio = total_comment_lines / len(non_blank_lines) if non_blank_lines else 0.0

    comment_score = 0.0
    if comment_pattern_hits > 0:
        comment_score += min(42.0, comment_weight_total * 1.4)
    if comment_ratio > 0.30:
        comment_score += min(18.0, (comment_ratio - 0.30) * 45.0)
        indicators.append({
            "name": "Unusual Comment Density",
            "severity": "medium",
            "description": f"Comment-to-code ratio is {int(comment_ratio * 100)}%, unusually high and typical of tutorial AI generations.",
            "line": None,
            "code_snippet": f"{total_comment_lines} comment lines out of {len(non_blank_lines)} total non-empty lines"
        })

    naming_hits = 0
    for pat in AI_NAMING_PATTERNS:
        matches = re.findall(pat, code)
        if matches:
            naming_hits += len(matches)
            for idx, line in enumerate(lines):
                if re.search(pat, line):
                    line_scores[idx] = max(line_scores[idx], 50.0)
                    if not line_reasons[idx]:
                        line_reasons[idx] = "Textbook AI variable/function naming pattern"

    naming_score = min(25.0, naming_hits * 5.0)
    if naming_hits >= 2:
        indicators.append({
            "name": "Textbook AI Identifiers",
            "severity": "medium" if naming_hits > 3 else "low",
            "description": f"Detected {naming_hits} occurrences of generic textbook identifiers (e.g. 'data_list', 'total_sum').",
            "line": None,
            "code_snippet": "Generic naming conventions"
        })

    scaffold_score = 0.0
    archetype_hits = 0
    archetype_weight_total = 0.0

    for pat, desc, weight in AI_ARCHETYPE_PATTERNS:
        matches = re.findall(pat, code)
        if matches:
            archetype_hits += len(matches)
            archetype_weight_total += weight * len(matches)
            for idx, line in enumerate(lines):
                if re.search(pat, line):
                    line_scores[idx] = max(line_scores[idx], min(95.0, weight * 4.0))
                    if not line_reasons[idx]:
                        line_reasons[idx] = desc
                    indicators.append({
                        "name": "Structural Archetype (Helpful Assistant)",
                        "severity": "high" if weight >= 18 else "medium",
                        "description": f"Detected '{desc}' on line {idx + 1}. Typical of LLM self-contained tutorial solutions.",
                        "line": idx + 1,
                        "code_snippet": line.strip()[:80]
                    })
                    break

    scaffold_score += min(32.0, archetype_weight_total * 0.8)

    generic_try = len(re.findall(r"except\s+Exception\s+as\s+e\s*:\s*(?:print|logger\.error|pass)", code))
    generic_try += len(re.findall(r"catch\s*\(\s*(?:error|err|e)\s*\)\s*\{\s*console\.(?:error|log)", code))
    if generic_try > 0:
        scaffold_score += min(15.0, generic_try * 7.5)
        indicators.append({
            "name": "Generic Exception Handler Boilerplate",
            "severity": "medium",
            "description": f"Detected {generic_try} textbook generic catch/except blocks commonly written by code generators.",
            "line": None,
            "code_snippet": "except Exception as e: print(f'Error: {e}')"
        })

    procedural_hits = 0
    for pat, desc, weight in AI_PROCEDURAL_PATTERNS:
        matches = re.findall(pat, code)
        if matches:
            procedural_hits += len(matches)
            for idx, line in enumerate(lines):
                if re.search(pat, line):
                    line_scores[idx] = max(line_scores[idx], min(95.0, weight * 4.0))
                    if not line_reasons[idx]:
                        line_reasons[idx] = desc
                    indicators.append({
                        "name": "Procedural Accumulator / Defensive Check",
                        "severity": "high" if weight >= 20 else "medium",
                        "description": f"Detected '{desc}' on line {idx + 1}. Typical of LLM safe logic templates.",
                        "line": idx + 1,
                        "code_snippet": line.strip()[:80]
                    })
                    break
    scaffold_score += min(25.0, procedural_hits * 10.0)

    entropy_score, entropy_metrics = analyze_entropy_and_regularity(lines)
    if entropy_metrics.get("uniformity_contribution", 0) > 8:
        indicators.append({
            "name": "Syntactic & Line Uniformity",
            "severity": "low",
            "description": f"Line length standard deviation ({entropy_metrics['std_line_length']} chars) is unnaturally clustered, typical of LLM decoders.",
            "line": None,
            "code_snippet": f"Uniformity score: {entropy_metrics['uniformity_contribution']}"
        })

    burst_score, burst_cv = analyze_burstiness(lines)
    if burst_score > 6.0:
        indicators.append({
            "name": "Flat Generation Burstiness",
            "severity": "medium",
            "description": f"Token variation coefficient ({burst_cv}) indicates flat, uniform token cadence rather than human burstiness.",
            "line": None,
            "code_snippet": f"Cadence CV: {burst_cv}"
        })

    complexity_mismatch = 0.0
    docstring_matches = re.findall(r'"""[\s\S]*?Args:[\s\S]*?Returns:[\s\S]*?"""', code)
    has_heavy_docstring = bool(docstring_matches)
    has_elementary_loop = bool(re.search(r"for\s+\w+\s+in\s+\w+:\s*\n\s*\w+\s*\+=\s*\w+", code))
    if has_heavy_docstring and has_elementary_loop:
        complexity_mismatch += 18.0
        indicators.append({
            "name": "Complexity Disparity (Over-Engineered Docs for Trivial Logic)",
            "severity": "medium",
            "description": "Found formal industrial-grade docstrings paired with elementary accumulation loop, characteristic of LLM instructional output.",
            "line": None,
            "code_snippet": "Formal docstring + elementary loop"
        })

    HUMAN_SCAR_PATTERNS = [
        (r"(?i)(#|//)\s*(todo|fixme|hack|xxx|temp\s*fix|workaround)\b", "Informal developer task/fix flag"),
        (r"(?m)^\s*(#|//)\s*(print\s*\(|console\.(?:log|warn)\s*\(|System\.out\.println)", "Commented-out debug print trace"),
        (r"(?m)^\s*(#|//)\s*([a-zA-Z_0-9]+\s*=\s*|def\s+|return\b)", "Commented-out trial code / dead line"),
        (r"(?i)(#|//)\s*(note\s*to\s*self|check\s*this|cleanup\s*later)", "Informal self-note")
    ]
    human_scars_found = []
    for pat, desc in HUMAN_SCAR_PATTERNS:
        matches = re.findall(pat, code)
        if matches:
            human_scars_found.extend([desc] * len(matches))

    human_scars_count = len(human_scars_found)
    human_damping_credit = 0.0
    if human_scars_count > 0:
        human_damping_credit = min(32.0, human_scars_count * 12.0)
        indicators.append({
            "name": "Iterative Development Scars (Human Signature)",
            "severity": "low",
            "description": f"Found {human_scars_count} traces of trial-and-error development (e.g. {human_scars_found[0]}). LLMs write pristine code in a single pass without iteration scars.",
            "line": None,
            "code_snippet": f"{human_scars_count} human development marker(s)"
        })

    function_defs = re.findall(r"(?m)^\s*def\s+([a-zA-Z_0-9]+)\s*\(", code)
    hyper_modular_count = 0
    if len(function_defs) >= 3 and len(non_blank_lines) < 25:
        hyper_modular_count = len(function_defs)
        indicators.append({
            "name": "Hyper-Modular Micro-Function Architecture",
            "severity": "medium",
            "description": f"Detected {len(function_defs)} micro-functions in a compact {len(non_blank_lines)}-line file. AI models habitually over-modularize simple logic.",
            "line": None,
            "code_snippet": f"{len(function_defs)} functions defined"
        })

    has_accumulator_sprawl = bool(re.search(r"(?m)^\s*([a-zA-Z_0-9]+)\s*=\s*0\s*\n\s*([a-zA-Z_0-9]+)\s*=\s*0", code))
    has_main_wrapper = bool(re.search(r'(?m)^\s*if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', code))
    has_mock_sample = bool(re.search(r'\b(sample_data|mock_data|records|test_data)\s*=\s*\[', code))
    has_tidy_print = bool(re.search(r'(?i)print\s*\(\s*(?:[a-zA-Z_0-9]+\s*\(|f?["\'])', code))
    is_helpful_assistant = has_main_wrapper and (has_mock_sample or has_tidy_print)

    syntax_score = 0.0
    syntax_hits = 0
    for pat, desc, weight in AI_SYNTAX_PATTERNS:
        matches = re.findall(pat, code)
        if matches:
            syntax_hits += len(matches)
            syntax_score += min(35.0, weight * len(matches))
            for idx, line in enumerate(lines):
                if re.search(pat, line):
                    line_scores[idx] = max(line_scores[idx], min(95.0, weight * 3.5))
                    if not line_reasons[idx]:
                        line_reasons[idx] = desc
                    indicators.append({
                        "name": "AI Syntactic / Idiomatic Pattern",
                        "severity": "high" if weight >= 22 else "medium",
                        "description": f"Found '{desc}' on line {idx + 1}.",
                        "line": idx + 1,
                        "code_snippet": line.strip()[:80]
                    })
                    break
    syntax_score = min(45.0, syntax_score)

    synergy_bonus = 0.0
    if comment_pattern_hits > 0 and naming_hits >= 2:
        synergy_bonus += 14.0
    if comment_pattern_hits > 0 and scaffold_score > 0:
        synergy_bonus += 12.0
    if syntax_hits >= 2:
        synergy_bonus += 15.0
    if syntax_hits >= 1 and naming_hits >= 1:
        synergy_bonus += 18.0

    raw_ai_score = comment_score + naming_score + scaffold_score + syntax_score + entropy_score + burst_score + complexity_mismatch + synergy_bonus - human_damping_credit

    if (syntax_hits >= 2 or (syntax_hits >= 1 and naming_hits >= 1)) and human_scars_count == 0:
        raw_ai_score = max(raw_ai_score, 82.0)

    final_score = max(4.0, min(97.5, raw_ai_score))

    if len(non_blank_lines) < 4 and not any("```" in l for l in lines) and syntax_hits == 0 and naming_hits == 0 and comment_pattern_hits == 0:
        final_score = min(final_score, 35.0)

    final_score = round(final_score, 1)

    factor_predictability = min(98.0, (naming_hits * 22.0) + (entropy_metrics.get("uniformity_contribution", 0) * 2.2) + (18.0 if naming_hits >= 1 else 3.0))
    if naming_hits == 0:
        factor_predictability = max(4.0, round(final_score * 0.18, 1))

    factor_burstiness = min(98.0, (burst_score * 3.8) + (entropy_metrics.get("uniformity_contribution", 0) * 2.0) + (20.0 if burst_cv < 0.35 and len(lines) > 5 else 4.0))
    if len(non_blank_lines) < 4:
        factor_burstiness = min(factor_burstiness, 22.0)

    factor_archetypes = min(98.0, (archetype_weight_total * 1.8) + (generic_try * 22.0) + (10.0 if archetype_hits > 0 else 2.0))
    if archetype_hits == 0 and generic_try == 0:
        factor_archetypes = max(3.0, round(final_score * 0.12, 1))

    raw_ml_prob = (factor_predictability * 0.35) + (factor_burstiness * 0.25) + (factor_archetypes * 0.25) + (comment_score * 0.15)
    factor_ml_classifiers = min(98.0, max(4.0, raw_ml_prob * (1.1 if synergy_bonus > 0 else 0.95)))

    factor_commenting = min(99.0, (comment_pattern_hits * 24.0) + (comment_ratio * 130.0))
    if total_comment_lines == 0:
        factor_commenting = 2.0

    factor_naming = min(98.0, naming_hits * 25.0)
    if naming_hits == 0:
        factor_naming = max(3.0, round(final_score * 0.15, 1))

    def get_stylometry_meta(score: float, dim_type: str) -> Dict[str, str]:
        if dim_type == "predictability":
            if score >= 70:
                return {
                    "status": "High Predictability (AI Path)",
                    "badge": "ai-flag",
                    "desc": "Tokens match standard LLM statistical path of least resistance. Smooth, textbook conventions without human shorthand.",
                    "ai_profile": "Smooth, completely uniform, follows path of least resistance.",
                    "human_profile": "Chaotic shorthand, quirky identifiers, lazy shortcuts."
                }
            if score >= 40:
                return {
                    "status": "Moderate Predictability",
                    "badge": "mixed-flag",
                    "desc": "Partial token clustering and standard textbook naming patterns observed.",
                    "ai_profile": "Partially uniform syntax flow.",
                    "human_profile": "Blend of standard and contextual identifiers."
                }
            return {
                "status": "Human Idiosyncratic",
                "badge": "human-flag",
                "desc": "Natural idiosyncratic developer shorthand and organic syntax shortcuts.",
                "ai_profile": "Defeated path of least resistance.",
                "human_profile": "Authentic human developer variable choices and style."
            }
        elif dim_type == "burstiness":
            if score >= 70:
                return {
                    "status": "Uniform Cadence (AI Flat)",
                    "badge": "ai-flag",
                    "desc": "Steady average complexity. Loops uniformly structured, nesting depth politely shallow and consistent.",
                    "ai_profile": "Politely shallow nesting, evenly spaced loops.",
                    "human_profile": "Convoluted one-liners mixed with sprawling blocks and abrupt returns."
                }
            if score >= 40:
                return {
                    "status": "Moderate Cadence",
                    "badge": "mixed-flag",
                    "desc": "Moderate variance in line lengths and expression density.",
                    "ai_profile": "Moderate token pacing.",
                    "human_profile": "Slight rhythm variation."
                }
            return {
                "status": "Wild Human Rhythm",
                "badge": "human-flag",
                "desc": "High burstiness variance: compact expressions mixed with abrupt control flow.",
                "ai_profile": "Defeated uniform cadence.",
                "human_profile": "Hyper-dense expressions alongside abrupt unceremonious returns."
            }
        elif dim_type == "archetypes":
            if score >= 70:
                return {
                    "status": "Helpful Assistant Boilerplate",
                    "badge": "ai-flag",
                    "desc": "Stereotypical entry point wrapper (`if __name__ == '__main__':`), mock data array, and tidy print statements.",
                    "ai_profile": "Self-contained solution with tidy test inputs and output formatting.",
                    "human_profile": "Isolated assignment functions without textbook test wrappers."
                }
            if score >= 40:
                return {
                    "status": "Standard Boilerplate",
                    "badge": "mixed-flag",
                    "desc": "Contains standard scaffolding or generic error catchers.",
                    "ai_profile": "Conventional project wrapper.",
                    "human_profile": "Contextual project integration."
                }
            return {
                "status": "Pure Assignment Logic",
                "badge": "human-flag",
                "desc": "Clean isolated function without artificial mock datasets or textbook wrappers.",
                "ai_profile": "Defeated helpful assistant syndrome.",
                "human_profile": "Realistic homework / assignment submission format."
            }
        else:                 
            if score >= 70:
                return {
                    "status": "High Neural Probability",
                    "badge": "ai-flag",
                    "desc": "Syntax tree probability distribution matches fine-tuned transformer classifiers (GPTZero, Turnitin, CopyLeaks, MOSS).",
                    "ai_profile": "Transformer attention heads detect cumulative LLM syntax flavor.",
                    "human_profile": "High-dimensional syntax distribution matches organic human code."
                }
            if score >= 40:
                return {
                    "status": "Ambiguous Probability",
                    "badge": "mixed-flag",
                    "desc": "Transformer embeddings fall in the borderline region between AI and assisted code.",
                    "ai_profile": "Mixed neural embedding signatures.",
                    "human_profile": "Borderline human-assisted syntax."
                }
            return {
                "status": "Passed Black Box Classifiers",
                "badge": "human-flag",
                "desc": "Cumulative syntax tree distribution passes Turnitin, GPTZero, CopyLeaks, and MOSS.",
                "ai_profile": "Bypassed transformer classifiers.",
                "human_profile": "Authentic organic syntax distribution."
            }

    stylometry_dimensions = {
        "predictability": {
            "name": "Predictability & Consistency (Perplexity)",
            "score": round(factor_predictability, 1),
            "icon": "🧠",
            **get_stylometry_meta(factor_predictability, "predictability")
        },
        "burstiness": {
            "name": "Rhythm & Variation (Burstiness)",
            "score": round(factor_burstiness, 1),
            "icon": "⚡",
            **get_stylometry_meta(factor_burstiness, "burstiness")
        },
        "structural_archetypes": {
            "name": "Structural Archetypes & Boilerplate",
            "score": round(factor_archetypes, 1),
            "icon": "🏛️",
            **get_stylometry_meta(factor_archetypes, "archetypes")
        },
        "ml_classifiers": {
            "name": "ML Classifiers (The Black Box - Turnitin & MOSS)",
            "score": round(factor_ml_classifiers, 1),
            "icon": "🔮",
            **get_stylometry_meta(factor_ml_classifiers, "ml_classifiers")
        }
    }

    six_factors = {
        "low_perplexity": stylometry_dimensions["predictability"],
        "rhythm_variation": stylometry_dimensions["burstiness"],
        "structural_archetypes": stylometry_dimensions["structural_archetypes"],
        "ml_classifiers": stylometry_dimensions["ml_classifiers"],
        "formal_commenting": {
            "name": "Excessive / Formal Commenting",
            "score": round(factor_commenting, 1),
            "icon": "💬",
            "status": "Robotic Annotations" if factor_commenting >= 70 else ("Formal Comments" if factor_commenting >= 40 else "Clean / Idiomatic"),
            "badge": "ai-flag" if factor_commenting >= 70 else ("mixed-flag" if factor_commenting >= 40 else "human-flag"),
            "desc": "Over-explains trivial code with step-by-step markers and instructional docstrings." if factor_commenting >= 40 else "Strictly zero comments or natural sparse code commentary."
        },
        "generic_naming": {
            "name": "Generic Naming Conventions",
            "score": round(factor_naming, 1),
            "icon": "🏷️",
            "status": "Generic Tropes" if factor_naming >= 70 else ("Mixed Identifiers" if factor_naming >= 40 else "Domain-Specific"),
            "badge": "ai-flag" if factor_naming >= 70 else ("mixed-flag" if factor_naming >= 40 else "human-flag"),
            "desc": "Stereotypical LLM textbook names (e.g., 'data_list', 'total_sum', 'calculate_total_sum')." if factor_naming >= 40 else "Concise contextual developer abbreviations (e.g., 'items', 'tot', 'res')."
        }
    }

    sig1_score = 2.0 if total_comment_lines == 0 else round(min(98.0, max(2.0, (comment_pattern_hits * 24.0) + (comment_ratio * 120.0) - (human_scars_count * 15.0))), 1)
    sig1_finding = "Strictly zero comments detected. Safe from Turnitin/MOSS commentary detectors." if total_comment_lines == 0 else (
        f"Detected {comment_pattern_hits} textbook AI commentary patterns across {total_comment_lines} comment lines." if comment_pattern_hits > 0 else
        f"Sparse natural comments ({total_comment_lines} lines)."
    )

    sig2_score = round(min(98.0, max(3.0, (naming_hits * 22.0) + (16.0 if naming_hits >= 1 else 3.0))), 1) if naming_hits > 0 else round(max(3.0, final_score * 0.15), 1)
    sig2_finding = f"Detected {naming_hits} textbook AI compound names (e.g. data_list, calculate_total, grade_records)." if naming_hits > 0 else "Authentic human variable naming: concise shorthand (e.g., items, rec, scores, cnt)."

    sig3_score = round(min(98.0, max(4.0, (generic_try * 35.0) + (procedural_hits * 16.0) + (10.0 if generic_try > 0 else 2.0))), 1) if (generic_try > 0 or procedural_hits > 0) else round(max(4.0, final_score * 0.12), 1)
    sig3_finding = "Contains generic try/except catchers and over-defensive boundary checks typical of AI safeguard prompts." if generic_try > 0 or procedural_hits > 1 else "Pragmatic, contextual error handling or clean bare-bones assertions."

    sig4_score = round(min(98.0, max(4.0, (entropy_metrics.get("uniformity_contribution", 0) * 2.4) + (15.0 if entropy_metrics.get("indent_regularity_ratio", 0) > 0.9 else 2.0))), 1)
    sig4_finding = f"Sterile indentation and uniform line lengths (std dev: {entropy_metrics.get('std_line_length', 0)} chars)." if sig4_score >= 50 else "High structural burstiness and natural spacing drift characteristic of human programmers."

    sig5_score = round(min(98.0, max(4.0, (hyper_modular_count * 25.0) + (14.0 if len(function_defs) > 2 and len(non_blank_lines) < 22 else 3.0))), 1)
    sig5_finding = f"Hyper-modular fragmentation ({len(function_defs)} micro-functions in small file)." if sig5_score >= 50 else "Clean contextual inline logic and Pythonic functional expressions."

    sig6_score = round(min(98.0, max(3.0, (archetype_weight_total * 1.8) + (24.0 if is_helpful_assistant else 2.0))), 1) if (archetype_hits > 0 or is_helpful_assistant) else round(max(3.0, final_score * 0.10), 1)
    sig6_finding = "Self-contained tutorial scaffold detected (if __name__ == '__main__' + mock array)." if is_helpful_assistant else "Pure isolated function without textbook tutorial scaffolding."

    sig7_score = round(min(98.0, max(4.0, (procedural_hits * 22.0) + (22.0 if has_accumulator_sprawl else 3.0))), 1) if (procedural_hits > 0 or has_accumulator_sprawl) else round(max(3.0, final_score * 0.14), 1)
    sig7_finding = "Procedural accumulator sprawl (total=0, count=0, list=[]) inside manual loops." if has_accumulator_sprawl else "Direct idiomatic aggregation via sum() and Pythonic list comprehensions."

    if human_scars_count > 0:
        sig8_score = round(max(4.0, min(18.0, 20.0 - human_scars_count * 5.0)), 1)
        sig8_finding = f"Found {human_scars_count} authentic developer iteration traces ({human_scars_found[0]}). Confirms ongoing human coding."
    else:
        sig8_score = round(min(95.0, max(14.0, (final_score * 0.72) + 12.0 if final_score > 40 else final_score * 0.35)), 1)
        sig8_finding = "Pristine first-draft code. Lacks commented-out experiments, dead lines, or informal TODO notes."

    sig9_score = round(min(98.0, max(4.0, (burst_score * 3.6) + (entropy_metrics.get("uniformity_contribution", 0) * 2.0) + (18.0 if burst_cv < 0.35 and len(lines) > 5 else 4.0))), 1)
    sig9_finding = f"Low token perplexity (path of least resistance) and uniform cadence (CV: {burst_cv})." if sig9_score >= 50 else "High token entropy and high-burstiness syntax variation."

    nine_signals = {
        "comments": {
            "id": "comments",
            "name": "1. Comment Footprint & Docstrings",
            "score": sig1_score,
            "verdict": "Robotic Commentary" if sig1_score >= 65 else ("Formal Comments" if sig1_score >= 35 else "Authentic / Zero Comments"),
            "badge": "ai-flag" if sig1_score >= 65 else ("mixed-flag" if sig1_score >= 35 else "human-flag"),
            "icon": "💬",
            "ai_behavior": "Over-explains obvious lines (# increment counter), docstrings on trivial functions, uniform spacing.",
            "human_behavior": "Sparse or 0% comments in homework; informal // TODO, // FIXME, commented-out dead code.",
            "finding": sig1_finding
        },
        "naming_conventions": {
            "id": "naming_conventions",
            "name": "2. Naming Conventions & Shorthand",
            "score": sig2_score,
            "verdict": "Textbook Tropes" if sig2_score >= 65 else ("Mixed Identifiers" if sig2_score >= 35 else "Human Shorthand"),
            "badge": "ai-flag" if sig2_score >= 65 else ("mixed-flag" if sig2_score >= 35 else "human-flag"),
            "icon": "🏷️",
            "ai_behavior": "Textbook compound names (user_data, calculate_total, is_valid), rarely abbreviates.",
            "human_behavior": "Mixed conventions (usr, tmp, x2, data2), personal shorthand, single-letter indices.",
            "finding": sig2_finding
        },
        "error_handling": {
            "id": "error_handling",
            "name": "3. Error Handling & Edge Cases",
            "score": sig3_score,
            "verdict": "Exhaustive Generic" if sig3_score >= 65 else ("Conventional Catch" if sig3_score >= 35 else "Pragmatic / Partial"),
            "badge": "ai-flag" if sig3_score >= 65 else ("mixed-flag" if sig3_score >= 35 else "human-flag"),
            "icon": "🛡️",
            "ai_behavior": "Generic try/except Exception as e or blanket catch; hyper-defensive .get() != None checks.",
            "human_behavior": "Partial error handling, specific errors hit during testing, or bare except: pass.",
            "finding": sig3_finding
        },
        "structure_formatting": {
            "id": "structure_formatting",
            "name": "4. Structure, Rhythm & Formatting",
            "score": sig4_score,
            "verdict": "Sterile Rhythm" if sig4_score >= 65 else ("Moderate Variation" if sig4_score >= 35 else "Organic Human Drift"),
            "badge": "ai-flag" if sig4_score >= 65 else ("mixed-flag" if sig4_score >= 35 else "human-flag"),
            "icon": "📐",
            "ai_behavior": "Sterile predictable indentation, identical blank-line rhythm, clustered line lengths.",
            "human_behavior": "Spacing drift, tighter grouping of related lines, high line-length variance.",
            "finding": sig4_finding
        },
        "code_organization": {
            "id": "code_organization",
            "name": "5. Code Organization & Modularity",
            "score": sig5_score,
            "verdict": "Hyper-Modular" if sig5_score >= 65 else ("Structured Modules" if sig5_score >= 35 else "Contextual Inline Logic"),
            "badge": "ai-flag" if sig5_score >= 65 else ("mixed-flag" if sig5_score >= 35 else "human-flag"),
            "icon": "🧩",
            "ai_behavior": "Breaks things into tiny micro-helpers; textbook factory abstractions even for 3 lines.",
            "human_behavior": "Contextual inline logic, consolidated functions that do related steps together.",
            "finding": sig5_finding
        },
        "boilerplate_imports": {
            "id": "boilerplate_imports",
            "name": "6. Boilerplate & Imports",
            "score": sig6_score,
            "verdict": "Helpful Scaffold" if sig6_score >= 65 else ("Standard Wrapper" if sig6_score >= 35 else "Clean Assignment Logic"),
            "badge": "ai-flag" if sig6_score >= 65 else ("mixed-flag" if sig6_score >= 35 else "human-flag"),
            "icon": "🏛️",
            "ai_behavior": "Neatly sorted imports, if __name__ == '__main__': with mock test data and neat prints.",
            "human_behavior": "Imports as needed (often unsorted/adhoc), runs code ad-hoc, isolated student function.",
            "finding": sig6_finding
        },
        "variable_lifecycle": {
            "id": "variable_lifecycle",
            "name": "7. Variable Lifecycle",
            "score": sig7_score,
            "verdict": "Procedural Accumulators" if sig7_score >= 65 else ("Standard Variables" if sig7_score >= 35 else "Idiomatic Reuse"),
            "badge": "ai-flag" if sig7_score >= 65 else ("mixed-flag" if sig7_score >= 35 else "human-flag"),
            "icon": "🔄",
            "ai_behavior": "Single-purpose accumulator sprawl (total=0, count=0, list=[]), manual element-by-element loops.",
            "human_behavior": "Reuses variables lazily, aggregates directly with sum()/comprehensions, mutates in place.",
            "finding": sig7_finding
        },
        "development_scars": {
            "id": "development_scars",
            "name": "8. Absence of Development Scars",
            "score": sig8_score,
            "verdict": "Single-Pass Perfection" if sig8_score >= 65 else ("Minor Traces" if sig8_score >= 35 else "Iterative Human Scars"),
            "badge": "ai-flag" if sig8_score >= 65 else ("mixed-flag" if sig8_score >= 35 else "human-flag"),
            "icon": "🩹",
            "ai_behavior": "First-draft perfection. Zero commented experiments, no dead code, no debug traces.",
            "human_behavior": "Traces of trial-and-error: // TODO, // FIXME, commented debug statements, scrap lines.",
            "finding": sig8_finding
        },
        "stylometric_cues": {
            "id": "stylometric_cues",
            "name": "9. Statistical & Stylometric Cues",
            "score": sig9_score,
            "verdict": "Low Perplexity AI" if sig9_score >= 65 else ("Moderate Entropy" if sig9_score >= 35 else "Wild Human Burstiness"),
            "badge": "ai-flag" if sig9_score >= 65 else ("mixed-flag" if sig9_score >= 35 else "human-flag"),
            "icon": "📊",
            "ai_behavior": "Low token perplexity (path of least resistance), clustered line length std dev, uniform indent.",
            "human_behavior": "High token burstiness, erratic line lengths, idiosyncratic whitespace and spacing drift.",
            "finding": sig9_finding
        }
    }

    if final_score < 20.0:
        verdict = "Human Written"
    elif final_score < 40.0:
        verdict = "Likely Human"
    elif final_score < 65.0:
        verdict = "Mixed / AI-Assisted"
    elif final_score < 85.0:
        verdict = "Likely AI-Generated"
    else:
        verdict = "Definitive AI Code"

    line_heatmaps = []
    base_line_bias = final_score * 0.4
    for idx, line in enumerate(lines):
        clean_l = line.strip()
        if not clean_l:
            line_heatmaps.append({
                "line_num": idx + 1,
                "text": line,
                "score": 0.0,
                "level": "empty",
                "reason": ""
            })
            continue

        calc_score = min(98.0, line_scores[idx] if line_scores[idx] > 0 else base_line_bias)
        calc_score = round(calc_score, 1)

        if calc_score > 65.0:
            level = "ai"
        elif calc_score > 35.0:
            level = "mixed"
        else:
            level = "human"

        line_heatmaps.append({
            "line_num": idx + 1,
            "text": line,
            "score": calc_score,
            "level": level,
            "reason": line_reasons[idx] or ("Consistent with AI syntax profile" if level == "ai" else "")
        })

    ai_family = detect_ai_model_family(code, language)

    return {
        "ai_score": final_score,
        "verdict": verdict,
        "language": language,
        "ai_family": ai_family,
        "universal_matrix": UNIVERSAL_NORMALIZER_MATRIX,
        "indicators": indicators,
        "six_factors": six_factors,
        "stylometry_dimensions": stylometry_dimensions,
        "nine_signals": nine_signals,
        "metrics": {
            "comment_score": round(comment_score, 1),
            "naming_score": round(naming_score, 1),
            "scaffold_score": round(scaffold_score, 1),
            "entropy_score": round(entropy_score, 1),
            "burst_score": round(burst_score, 1),
            "complexity_score": round(complexity_mismatch, 1),
            "comment_ratio": round(comment_ratio * 100, 1),
            "human_damping_credit": round(human_damping_credit, 1),
            **entropy_metrics,
            "burst_cv": burst_cv
        },
        "line_heatmaps": line_heatmaps
    }
