# Recommended AI Models for Your Intel 12th Gen (8 GB RAM)

Running large 7B–14B models on an 8 GB Windows machine leads to heavy memory exhaustion and freezes the system. However, the latest ultra-compact 1.5B–3B models offer incredible coding and chat performance while consuming **less than 2 GB of RAM**, leaving 6 GB of headroom for Windows and your development tasks.

---

## Top Recommended Models for Your Hardware

| Model | Size in RAM | Speed on i5-1235U | Best For |
| :--- | :--- | :--- | :--- |
| **Qwen 2.5 Coder 1.5B** (`qwen2.5-coder:1.5b`) | **~1.1 GB** | 45–60 tokens/sec | Instant code completion, C++, DSA, scripts |
| **Qwen 2.5 Coder 3B** (`qwen2.5-coder:3b`) | **~2.2 GB** | 30–40 tokens/sec | High accuracy logic, full function writing |
| **Phi-3.5 Mini 3.8B** (`phi3.5:latest`) | **~2.4 GB** | 25–35 tokens/sec | Reasoning, conversational Q&A |
| **DeepSeek R1 1.5B** (`deepseek-r1:1.5b`) | **~1.2 GB** | 40–55 tokens/sec | Chain-of-thought mathematical and algorithmic reasoning |

---

## 1-Minute Setup via Ollama

1. **Install Ollama** (if not already installed):
   Download and run the installer from: [ollama.com/download/windows](https://ollama.com/download/windows)

2. **Pull and Run the Fastest Coding Model**:
   Open a terminal and run:
   ```bash
   ollama run qwen2.5-coder:1.5b
   ```
   *This downloads in under 1 minute and uses only ~1 GB RAM.*

3. **For Deep Algorithmic Reasoning (DSA / Competitive Programming)**:
   ```bash
   ollama run deepseek-r1:1.5b
   ```

4. **Integration with VS Code**:
   - Install the **Continue** or **Twinny** extension in VS Code.
   - Point the provider to `http://localhost:11434` with model `qwen2.5-coder:1.5b`.
   - You now have an offline, zero-latency, private copilot running directly on your Intel Iris Xe / CPU without lagging your PC!
