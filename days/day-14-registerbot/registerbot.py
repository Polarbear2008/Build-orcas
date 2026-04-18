"""
ORCAS-7 RegisterBot: Advanced CPU Simulator
Day 14 - Computer Architecture Implementation

A high-fidelity simulation of a Load-Store architecture CPU with a built-in 
ALU and LLM-assisted diagnostic narration (ORCAS-7 Kernel).
"""

import subprocess
import sys
import time
from typing import Dict, List, Union, Tuple, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.theme import Theme
    
    # Custom Cyberpunk Theme
    cyber_theme = Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "cpu.reg": "bold green",
        "cpu.val": "cyan",
        "cpu.pc": "magenta",
        "cpu.op": "bold yellow",
        "kernel": "bold green",
    })
    console = Console(theme=cyber_theme)
except ImportError:
    print("Error: 'rich' package required. Run: pip install rich")
    sys.exit(1)

# Configuration
MODEL = "qwen2.5:3b"
CYBER_GREEN = "#00ff41"
DEEP_SLATE = "#1e1e1e"

# -----------------------------------------------------------------------------
# CPU ARCHITECTURE
# -----------------------------------------------------------------------------

class CPU:
    """Simulates a physical CPU with registers, ALU, and Flags."""
    
    def __init__(self, num_registers: int = 8):
        self.registers = [0] * num_registers
        self.pc = 0
        self.flags = {"ZERO": False, "NEG": False}
        self.halted = False
        self.program = []
        self.cycle_count = 0
        self.last_effect = "INITIALIZED"
        self.history = []  # Trace of executed instructions

    def reset(self):
        self.__init__(len(self.registers))

    def load(self, program: List[List[str]]):
        self.program = program

    def is_register(self, s: str) -> bool:
        return s.startswith("R") and s[1:].isdigit()

    def get_reg_idx(self, s: str) -> int:
        idx = int(s[1:])
        if idx >= len(self.registers):
            raise IndexError(f"Register {s} out of bounds")
        return idx

    def get_val(self, arg: str) -> int:
        if self.is_register(arg):
            return self.registers[self.get_reg_idx(arg)]
        return int(arg)

# -----------------------------------------------------------------------------
# ALU & INSTRUCTION DECODER
# -----------------------------------------------------------------------------

def alu_op(op: str, a: int, b: Optional[int] = None) -> int:
    """The Arithmetic Logic Unit."""
    ops = {
        "ADD": lambda x, y: x + y,
        "SUB": lambda x, y: x - y,
        "MUL": lambda x, y: x * y,
        "DIV": lambda x, y: x // y if y != 0 else 0,
        "AND": lambda x, y: x & y,
        "OR":  lambda x, y: x | y,
        "XOR": lambda x, y: x ^ y,
        "NOT": lambda x, _: ~x,
        "INC": lambda x, _: x + 1,
        "DEC": lambda x, _: x - 1,
    }
    if op not in ops:
        raise ValueError(f"Unknown ALU op: {op}")
    return ops[op](a, b or 0)

def step_cpu(cpu: CPU) -> Tuple[List[str], str]:
    """Fetch-Decode-Execute Cycle."""
    if cpu.pc >= len(cpu.program):
        cpu.halted = True
        return [], "EOF"

    instr = cpu.program[cpu.pc]
    op = instr[0].upper()
    args = instr[1:]
    
    try:
        if op == "MOV":
            dst = cpu.get_reg_idx(args[0])
            val = cpu.get_val(args[1])
            cpu.registers[dst] = val
            effect = f"R{dst} ← {val}"
            cpu.pc += 1
            
        elif op in ("ADD", "SUB", "MUL", "DIV", "AND", "OR", "XOR"):
            dst_idx = cpu.get_reg_idx(args[0])
            a = cpu.registers[dst_idx]
            b = cpu.get_val(args[1])
            res = alu_op(op, a, b)
            cpu.registers[dst_idx] = res
            effect = f"R{dst_idx} = {a} {op} {b} → {res}"
            cpu.pc += 1
            
        elif op in ("NOT", "INC", "DEC"):
            dst_idx = cpu.get_reg_idx(args[0])
            a = cpu.registers[dst_idx]
            res = alu_op(op, a)
            cpu.registers[dst_idx] = res
            effect = f"R{dst_idx} = {op}({a}) → {res}"
            cpu.pc += 1

        elif op == "CMP":
            a = cpu.get_val(args[0])
            b = cpu.get_val(args[1])
            cpu.flags["ZERO"] = (a == b)
            cpu.flags["NEG"] = (a < b)
            effect = f"CMP {a}, {b} → Z:{cpu.flags['ZERO']} N:{cpu.flags['NEG']}"
            cpu.pc += 1

        elif op == "JMP":
            target = int(args[0])
            cpu.pc = target
            effect = f"JUMP → ADR:{target}"

        elif op == "JZ":
            target = int(args[0])
            if cpu.flags["ZERO"]:
                cpu.pc = target
                effect = f"JZ TAKEN → ADR:{target}"
            else:
                cpu.pc += 1
                effect = "JZ SKIPPED"

        elif op == "JNZ":
            target = int(args[0])
            if not cpu.flags["ZERO"]:
                cpu.pc = target
                effect = f"JNZ TAKEN → ADR:{target}"
            else:
                cpu.pc += 1
                effect = "JNZ SKIPPED"

        elif op == "HALT":
            cpu.halted = True
            effect = "SYSTEM HALTED"
            
        else:
            effect = f"ERROR: Unknown OP {op}"
            cpu.pc += 1
            
    except Exception as e:
        effect = f"FAULT: {e}"
        cpu.halted = True

    cpu.cycle_count += 1
    cpu.last_effect = effect
    cpu.history.append(f"[{cpu.cycle_count:03d}] {' '.join(instr)} | {effect}")
    return instr, effect

# -----------------------------------------------------------------------------
# LLM NARRATION (ORCAS-7 Kernel Internal Thought)
# -----------------------------------------------------------------------------

NARRATOR_PROMPT = """You are the ORCAS-7 Kernel, a low-level diagnostic AI.
Briefly explain the current CPU state transition in professional, technical language.
Instruction: {instr}
ALU Effect: {effect}
Registers: {regs}
Flags: {flags}

Respond with EXACTLY one sentence (max 15 words). Focus on hardware implications."""

def narrate(instr: List[str], effect: str, cpu: CPU) -> str:
    """Query Ollama for system narration."""
    regs_str = ", ".join(f"R{i}:{v}" for i, v in enumerate(cpu.registers) if v != 0) or "NUL"
    prompt = NARRATOR_PROMPT.format(
        instr=" ".join(instr),
        effect=effect,
        regs=regs_str,
        flags=f"Z:{int(cpu.flags['ZERO'])} N:{int(cpu.flags['NEG'])}"
    )
    
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return "System narration unavailable. Kernel monitoring offline."

# -----------------------------------------------------------------------------
# USER INTERFACE (Rich Dashboard)
# -----------------------------------------------------------------------------

def make_layout() -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=5)
    )
    layout["main"].split_row(
        Layout(name="side", size=25),
        Layout(name="body")
    )
    layout["body"].split_column(
        Layout(name="code", size=12),
        Layout(name="trace")
    )
    return layout

def update_display(layout: Layout, cpu: CPU, instr: List[str], effect: str, narration: str):
    # Header
    layout["header"].update(Panel(
        Align.center(f"[bold cyan]ORCAS-7 SYSTEM INTERFACE[/bold cyan] | [magenta]PC: {cpu.pc:03d}[/magenta] | [green]CYCLES: {cpu.cycle_count:03d}[/green]"),
        style="white on blue", border_style="cyan"
    ))
    
    # Sidebar: Registers
    reg_table = Table(title="REGISTER BANK", box=None, expand=True)
    reg_table.add_column("REG", style="dim")
    reg_table.add_column("VAL", justify="right", style="cpu.val")
    for i, val in enumerate(cpu.registers):
        reg_table.add_row(f"R{i}", str(val))
    
    flags_text = Text.assemble(
        ("\nFLAGS\n", "bold"),
        (f"ZERO: {int(cpu.flags['ZERO'])}\n", "green" if cpu.flags["ZERO"] else "dim"),
        (f"NEG:  {int(cpu.flags['NEG'])}", "red" if cpu.flags["NEG"] else "dim")
    )
    
    layout["side"].update(Panel(Align.center(reg_table), title="HARDWARE", border_style="green"))
    
    # Main Body: Instruction & Code
    code_text = Text()
    for i, prog_instr in enumerate(cpu.program):
        ptr = "► " if i == cpu.pc else "  "
        style = "bold yellow" if i == cpu.pc else "dim"
        code_text.append(f"{ptr}{i:02d}: {' '.join(prog_instr)}\n", style=style)
        
    layout["code"].update(Panel(code_text, title="PROGRAM MEMORY", border_style="yellow"))
    
    # Trace/History
    trace_text = "\n".join(cpu.history[-10:])
    layout["trace"].update(Panel(trace_text, title="ALU EXECUTION TRACE", border_style="magenta"))
    
    # Footer: LLM Narration
    layout["footer"].update(Panel(
        f"[kernel]K-OS >[/kernel] {narration or 'Waiting for cycle...'}",
        title="KERNEL DIAGNOSTICS", border_style="green"
    ))

# -----------------------------------------------------------------------------
# RUNTIME
# -----------------------------------------------------------------------------

PROGRAM_FACTORIAL = [
    ["MOV", "R0", "5"],   # counter
    ["MOV", "R1", "1"],   # result
    ["MOV", "R2", "0"],   # constant 0
    ["MOV", "R3", "1"],   # constant 1
    ["CMP", "R0", "R2"],  # loop check
    ["JZ",  "9"],         # exit if 0
    ["MUL", "R1", "R0"],  # res *= counter
    ["SUB", "R0", "R3"],  # counter -= 1
    ["JMP", "4"],         # loop
    ["HALT"]
]

def main():
    cpu = CPU()
    cpu.load(PROGRAM_FACTORIAL)
    
    layout = make_layout()
    narration = ""
    
    with Live(layout, refresh_per_second=4, screen=True) as live:
        while not cpu.halted and cpu.cycle_count < 100:
            instr, effect = step_cpu(cpu)
            if instr:
                narration = narrate(instr, effect, cpu)
            update_display(layout, cpu, instr, effect, narration)
            time.sleep(0.8)
            
        time.sleep(2)  # Let user see final state
    
    console.print(Panel(
        Align.center(f"[bold green]EXECUTION COMPLETE[/bold green]\nFinal Result (R1): [bold cyan]{cpu.registers[1]}[/bold cyan]"),
        border_style="green", padding=(1, 2)
    ))

if __name__ == "__main__":
    main()