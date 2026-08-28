"""Small shared visual foundation for Mateo Trucco desktop apps."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

PALETTE={"bg":"#f3f6fb","card":"#ffffff","ink":"#17233c","muted":"#5b6980","line":"#ced8e7","accent":"#2563eb","accent_hover":"#174eb4","soft":"#eaf1fb"}

def apply_theme(root:tk.Tk,accent:str|None=None)->dict[str,str]:
    colors={**PALETTE,"accent":accent or PALETTE["accent"]};root.configure(bg=colors["bg"])
    style=ttk.Style(root);style.theme_use("clam")
    style.configure("TFrame",background=colors["bg"]);style.configure("Card.TFrame",background=colors["card"])
    style.configure("TLabel",background=colors["bg"],foreground=colors["ink"],font=("Segoe UI",10));style.configure("Card.TLabel",background=colors["card"],foreground=colors["ink"]);style.configure("Muted.TLabel",foreground=colors["muted"]);style.configure("Title.TLabel",font=("Segoe UI Variable Display",24,"bold"),foreground=colors["ink"])
    style.configure("TButton",padding=(13,9),background=colors["card"],foreground=colors["ink"],bordercolor=colors["line"],font=("Segoe UI",10,"bold"));style.map("TButton",background=[("active",colors["soft"])],bordercolor=[("active",colors["accent"])])
    style.configure("Accent.TButton",background=colors["accent"],foreground="white",bordercolor=colors["accent"]);style.map("Accent.TButton",background=[("active",colors["accent_hover"])])
    style.configure("TLabelframe",background=colors["card"],bordercolor=colors["line"],relief="solid");style.configure("TLabelframe.Label",background=colors["card"],foreground=colors["ink"],font=("Segoe UI",10,"bold"));style.configure("TEntry",fieldbackground=colors["card"],foreground=colors["ink"],bordercolor=colors["line"],padding=8);style.configure("TRadiobutton",background=colors["bg"],foreground=colors["ink"]);style.configure("TCheckbutton",background=colors["bg"],foreground=colors["ink"])
    return colors

def text_style(widget:tk.Text,colors:dict[str,str],readonly:bool=False)->None:
    widget.configure(bg=colors["card"],fg=colors["ink"],insertbackground=colors["accent"],selectbackground=colors["accent"],selectforeground="white",relief="flat",highlightthickness=1,highlightbackground=colors["line"],highlightcolor=colors["accent"])
    if readonly:widget.configure(state="disabled")
