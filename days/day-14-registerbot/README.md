# Day 14: RegisterBot (CPU Simulator)

A high-fidelity CPU simulator built from scratch. It features a Load-Store architecture, a functional ALU, and a real-time terminal dashboard.

## 🚀 Features
- **8-Register CPU**: Simulates physical hardware registers (R0-R7).
- **Advanced ISA**: Supports `MOV`, `ADD`, `SUB`, `MUL`, `DIV`, `CMP`, `JMP`, `JZ`, `JNZ`, `AND`, `OR`, `XOR`, `NOT`, `INC`, `DEC`, and `HALT`.
- **ORCAS-7 Kernel**: A local LLM (Ollama) that narrates every CPU cycle with technical diagnostics.
- **Rich Dashboard**: Real-time visualization of registers, program memory, and execution trace.

## 🛠️ Requirements
- Python 3.9+
- [Ollama](https://ollama.com/) (running `qwen2.5:3b`)
- `rich` library

## 🏃 How to Run
1. **Activate Environment**:
   ```bash
   source ../../.venv/bin/activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install rich
   ```
3. **Pull the AI Model**:
   ```bash
   ollama pull qwen2.5:3b
   ```
4. **Start the Simulator**:
   ```bash
   python registerbot.py
   ```

## 📄 Demo Program
The simulator is pre-loaded with a **Factorial Algorithm** (calculating 5! = 120) using conditional jumps and register arithmetic.
