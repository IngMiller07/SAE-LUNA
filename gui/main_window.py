"""
SAE - Sistema de Alertas Estudiantiles
Interfaz Principal (CustomTkinter)
Módulos: Dashboard, Chat IA (Luna), Gestión de Alertas, Reportes PDF, Visión YOLO
"""
import os
import sys
import threading
import time
import customtkinter as ctk
import cv2
from PIL import Image
from tkinter import messagebox

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from database import get_session
from models import Estudiante, Alerta, Seguimiento
from ai_core.vision_yolo import VisionMonitor
from ai_core.rag_chatbot import get_chatbot
from reports.pdf_generator import generar_reporte_riesgos

# ══════════════════════════════════════════
#  PALETA DE COLORES (Dark Premium)
# ══════════════════════════════════════════
C_BG        = "#0d1117"
C_SIDEBAR   = "#161b22"
C_CARD      = "#21262d"
C_CARD2     = "#2d333b"
C_ACCENT    = "#2563eb"
C_ACCENTHOV = "#1d4ed8"
C_GREEN     = "#238636"
C_GREENHOV  = "#1a7f37"
C_RED       = "#da3633"
C_ORANGE    = "#d97706"
C_TEXT      = "#e6edf3"
C_MUTED     = "#8b949e"
C_BORDER    = "#30363d"
C_BUBBLE_AI = "#1c2128"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ══════════════════════════════════════════
#  COMPONENTES REUTILIZABLES
# ══════════════════════════════════════════
class KpiCard(ctk.CTkFrame):
    """Tarjeta de métrica con barra de color superior."""
    def __init__(self, parent, label, value="0", accent=C_ACCENT):
        super().__init__(parent, fg_color=C_CARD, corner_radius=10,
                         border_width=1, border_color=C_BORDER)
        # Barra coloreada
        bar = ctk.CTkFrame(self, fg_color=accent, height=4, corner_radius=2)
        bar.pack(fill="x")
        # Valor
        self._lbl_val = ctk.CTkLabel(self, text=str(value),
                                     font=ctk.CTkFont("Segoe UI", 36, "bold"),
                                     text_color=accent)
        self._lbl_val.pack(pady=(12, 2))
        # Etiqueta
        ctk.CTkLabel(self, text=label, font=ctk.CTkFont("Segoe UI", 11),
                     text_color=C_MUTED).pack(pady=(0, 14))

    def set(self, value):
        self._lbl_val.configure(text=str(value))


class NavBtn(ctk.CTkButton):
    """Botón de navegación en sidebar."""
    def __init__(self, parent, icon, label, command):
        super().__init__(parent, text=f"  {icon}  {label}", anchor="w",
                         fg_color="transparent", text_color=C_MUTED,
                         hover_color=C_CARD2, font=ctk.CTkFont("Segoe UI", 13),
                         height=44, corner_radius=8, command=command)

    def activate(self):
        self.configure(fg_color=C_CARD2, text_color=C_TEXT)

    def deactivate(self):
        self.configure(fg_color="transparent", text_color=C_MUTED)


# ══════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════
class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SAE — Sistema de Alertas Estudiantiles v2.0")
        self.geometry("1360x830")
        self.minsize(1100, 700)
        self.configure(fg_color=C_BG)

        # Grid raiz: sidebar | contenido
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._nav_btns: dict[str, NavBtn] = {}
        self._active = None
        self._rag = None      # instancia de RAGChatbot
        self._rag_ok = False  # listo para responder
        self._cam_running = False

        self._build_sidebar()
        self._build_content_area()
        self._load_rag_bg()
        self._show("dashboard")

    # ──────────────────────────────────────
    #  SIDEBAR
    # ──────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=250, fg_color=C_SIDEBAR, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(6, weight=1)

        # Logo
        ctk.CTkLabel(sb, text="📚  SAE v2.0",
                     font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     text_color=C_TEXT).grid(row=0, column=0, padx=24, pady=(30, 20), sticky="w")

        # Divisor
        ctk.CTkFrame(sb, height=1, fg_color=C_BORDER).grid(row=1, column=0, padx=15, sticky="ew")

        # Botones de navegacion
        views = [
            ("dashboard", "📊", "Dashboard"),
            ("chat",      "🤖", "Luna — IA Académica"),
            ("alertas",   "🚨", "Gestión de Alertas"),
            ("reportes",  "📄", "Reportes PDF"),
            ("vision",    "👁️",  "Monitoreo YOLO"),
        ]
        for row_i, (vid, icon, lbl) in enumerate(views, start=2):
            btn = NavBtn(sb, icon, lbl, command=lambda v=vid: self._show(v))
            btn.grid(row=row_i, column=0, padx=10, pady=2, sticky="ew")
            self._nav_btns[vid] = btn

        # Status IA
        self._lbl_ia = ctk.CTkLabel(sb, text="⚙ IA: Iniciando…",
                                    font=ctk.CTkFont("Segoe UI", 11),
                                    text_color=C_MUTED)
        self._lbl_ia.grid(row=7, column=0, padx=20, pady=20, sticky="w")

    # ──────────────────────────────────────
    #  AREA DE CONTENIDO (frame contenedor)
    # ──────────────────────────────────────
    def _build_content_area(self):
        self._content = ctk.CTkFrame(self, fg_color=C_BG, corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

        # Construir todas las "páginas" (ocultas al inicio)
        self._pages: dict = {}
        self._pages["dashboard"] = self._mk_dashboard()
        self._pages["chat"]      = self._mk_chat()
        self._pages["alertas"]   = self._mk_alertas()
        self._pages["reportes"]  = self._mk_reportes()
        self._pages["vision"]    = self._mk_vision()

        for pg in self._pages.values():
            pg.grid(row=0, column=0, sticky="nsew")
            pg.grid_remove()   # todas ocultas

    def _show(self, name: str):
        if self._active == name:
            return
        # Ocultar actual
        if self._active:
            self._pages[self._active].grid_remove()
            self._nav_btns[self._active].deactivate()
        # Mostrar nueva
        self._pages[name].grid()
        self._nav_btns[name].activate()
        self._active = name

        # Refresh dinámico
        refresh_map = {
            "dashboard": self._refresh_dashboard,
            "alertas":   self._refresh_alertas,
        }
        if name in refresh_map:
            refresh_map[name]()

    # ══════════════════════════════════════════
    #  PÁGINA: DASHBOARD
    # ══════════════════════════════════════════
    def _mk_dashboard(self):
        pg = ctk.CTkFrame(self._content, fg_color=C_BG)
        pg.grid_columnconfigure(0, weight=1)
        pg.grid_rowconfigure(2, weight=1)

        # Header
        hdr = ctk.CTkFrame(pg, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="ew")
        ctk.CTkLabel(hdr, text="Dashboard Analítico",
                     font=ctk.CTkFont("Segoe UI", 26, "bold"),
                     text_color=C_TEXT).pack(side="left")

        # KPI Cards
        kpi_row = ctk.CTkFrame(pg, fg_color="transparent")
        kpi_row.grid(row=1, column=0, padx=30, pady=0, sticky="ew")
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1, uniform="kpi")

        self._kpi_total  = KpiCard(kpi_row, "Estudiantes",     accent=C_ACCENT)
        self._kpi_alto   = KpiCard(kpi_row, "Riesgo Alto",      accent=C_RED)
        self._kpi_medio  = KpiCard(kpi_row, "Riesgo Medio",     accent=C_ORANGE)
        self._kpi_alert  = KpiCard(kpi_row, "Alertas Activas",  accent=C_RED)
        for col, card in enumerate([self._kpi_total, self._kpi_alto,
                                    self._kpi_medio, self._kpi_alert]):
            card.grid(row=0, column=col, padx=6, pady=0, sticky="nsew")

        # Tabla de estudiantes críticos
        lbl_sec = ctk.CTkLabel(pg, text="Estudiantes con Riesgo Alto",
                               font=ctk.CTkFont("Segoe UI", 16, "bold"),
                               text_color=C_TEXT)
        lbl_sec.grid(row=2, column=0, padx=35, pady=(30, 8), sticky="w")

        self._tabla_dash = ctk.CTkScrollableFrame(pg, fg_color=C_CARD,
                                                  corner_radius=10)
        self._tabla_dash.grid(row=3, column=0, padx=30, pady=(0, 30),
                              sticky="nsew")
        pg.grid_rowconfigure(3, weight=1)
        pg.grid_rowconfigure(2, weight=0)
        return pg

    def _refresh_dashboard(self):
        s = get_session()
        try:
            total  = s.query(Estudiante).count()
            altos  = s.query(Estudiante).filter_by(nivel_riesgo="Alto").all()
            medio  = s.query(Estudiante).filter_by(nivel_riesgo="Medio").count()
            actvas = s.query(Alerta).filter_by(estado="Activa").count()

            self._kpi_total.set(total)
            self._kpi_alto.set(len(altos))
            self._kpi_medio.set(medio)
            self._kpi_alert.set(actvas)

            # Limpiar tabla
            for w in self._tabla_dash.winfo_children():
                w.destroy()

            # Cabecera tabla
            cols = ["Nombre", "Carrera", "Semestre", "Promedio", "Asistencia", "Riesgo"]
            widths = [200, 200, 80, 90, 90, 90]
            hdr = ctk.CTkFrame(self._tabla_dash, fg_color=C_CARD2)
            hdr.pack(fill="x", padx=5, pady=(5, 0))
            for j, (c, w) in enumerate(zip(cols, widths)):
                ctk.CTkLabel(hdr, text=c, width=w,
                             font=ctk.CTkFont("Segoe UI", 11, "bold"),
                             text_color=C_MUTED).pack(side="left", padx=8, pady=6)

            # Filas
            for i, e in enumerate(altos):
                bg = C_CARD if i % 2 == 0 else C_CARD2
                row = ctk.CTkFrame(self._tabla_dash, fg_color=bg)
                row.pack(fill="x", padx=5, pady=1)
                vals = [e.nombre, e.carrera[:28], str(e.semestre),
                        f"{e.promedio:.1f}", f"{e.asistencia:.0f}%", e.nivel_riesgo]
                for val, w in zip(vals, widths):
                    ctk.CTkLabel(row, text=val, width=w,
                                 text_color=C_TEXT if val != "Alto" else C_RED,
                                 font=ctk.CTkFont("Segoe UI", 12)).pack(
                                     side="left", padx=8, pady=7)

            if not altos:
                ctk.CTkLabel(self._tabla_dash, text="✅  No hay estudiantes en riesgo alto.",
                             text_color=C_MUTED).pack(pady=30)
        finally:
            s.close()

    # ══════════════════════════════════════════
    #  PÁGINA: CHAT LUNA
    # ══════════════════════════════════════════
    def _mk_chat(self):
        pg = ctk.CTkFrame(self._content, fg_color=C_BG)
        pg.grid_columnconfigure(0, weight=1)
        pg.grid_rowconfigure(0, weight=1)

        # Área de historial (scroll)
        self._chat_scroll = ctk.CTkScrollableFrame(pg, fg_color="transparent",
                                                   scrollbar_button_color=C_CARD2)
        self._chat_scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Banner de bienvenida (se destruye al primer mensaje)
        self._banner = ctk.CTkFrame(self._chat_scroll, fg_color="transparent")
        self._banner.pack(expand=True, pady=60)
        ctk.CTkLabel(self._banner, text="🤖",
                     font=ctk.CTkFont(size=52)).pack()
        ctk.CTkLabel(self._banner, text="Hola, soy Luna",
                     font=ctk.CTkFont("Segoe UI", 26, "bold"),
                     text_color=C_TEXT).pack(pady=(10, 4))
        ctk.CTkLabel(self._banner,
                     text="Tu asistente académico con IA. Haz cualquier pregunta.",
                     text_color=C_MUTED).pack()

        # Sugerencias rápidas
        sug_f = ctk.CTkFrame(self._banner, fg_color="transparent")
        sug_f.pack(pady=24)
        sugs = [
            "¿Quiénes están en riesgo alto?",
            "Técnicas de estudio recomendadas",
            "¿Cómo funciona el sistema SAE?",
            "Plan de mejoramiento para estudiante",
        ]
        for i, s in enumerate(sugs):
            btn = ctk.CTkButton(sug_f, text=s, fg_color=C_CARD, hover_color=C_CARD2,
                                border_width=1, border_color=C_BORDER,
                                text_color=C_TEXT, corner_radius=8,
                                command=lambda txt=s: self._chat_send(txt))
            btn.grid(row=i // 2, column=i % 2, padx=8, pady=6, sticky="ew")

        # Frame de entrada fijo abajo
        inp = ctk.CTkFrame(pg, fg_color=C_CARD, corner_radius=14,
                           border_width=1, border_color=C_BORDER)
        inp.grid(row=1, column=0, sticky="ew", padx=80, pady=(0, 28))

        self._chat_input = ctk.CTkTextbox(inp, height=46,
                                          font=ctk.CTkFont("Segoe UI", 14),
                                          fg_color="transparent",
                                          text_color=C_TEXT,
                                          scrollbar_button_color=C_CARD)
        self._chat_input.pack(side="left", expand=True, fill="both",
                              padx=16, pady=8)
        self._chat_input.bind("<Return>",
                              lambda e: self._handle_enter(e))
        self._chat_input.bind("<Shift-Return>", lambda e: "break")

        ctk.CTkButton(inp, text="↑ Enviar", width=88, height=36,
                      fg_color=C_ACCENT, hover_color=C_ACCENTHOV,
                      font=ctk.CTkFont("Segoe UI", 13, "bold"),
                      corner_radius=10,
                      command=lambda: self._chat_send()).pack(
                          side="right", padx=12, pady=8)
        return pg

    def _handle_enter(self, event):
        if not (event.state & 0x0001):   # Sin Shift
            self._chat_send()
            return "break"

    def _chat_send(self, preset: str = None):
        text = preset or self._chat_input.get("1.0", "end-1c").strip()
        if not text:
            return
        self._chat_input.delete("1.0", "end")

        # Quitar banner si existe
        if self._banner and self._banner.winfo_exists():
            self._banner.pack_forget()
            self._banner = None

        self._add_bubble(text, is_ai=False)

        if not self._rag_ok:
            self._add_bubble(
                "Estoy cargando Ollama y el índice RAG, por favor espera un momento e intenta de nuevo. "
                "(Si el error persiste, asegúrate de que Ollama esté corriendo en localhost:11434)",
                is_ai=True, warning=True
            )
            return

        self._add_typing()
        threading.Thread(target=self._process_chat,
                         args=(text,), daemon=True).start()

    def _process_chat(self, txt: str):
        try:
            resp = self._rag.ask(txt)
        except Exception as e:
            resp = f"Error técnico al consultar la IA: {e}"

        def _ui():
            if hasattr(self, "_typing_msg") and self._typing_msg.winfo_exists():
                self._typing_msg.destroy()
            self._add_bubble(resp, is_ai=True)
        self.after(0, _ui)

    def _add_bubble(self, text: str, is_ai: bool, warning: bool = False):
        row = ctk.CTkFrame(self._chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=6)

        if is_ai:
            bubble = ctk.CTkFrame(row, fg_color=C_BUBBLE_AI, corner_radius=12)
            bubble.pack(anchor="w", padx=20, fill="x")
            ctk.CTkLabel(bubble,
                         text="🤖 Luna",
                         font=ctk.CTkFont("Segoe UI", 11, "bold"),
                         text_color=C_ACCENT if not warning else C_ORANGE
                         ).pack(anchor="w", padx=14, pady=(10, 2))
        else:
            bubble = ctk.CTkFrame(row, fg_color=C_CARD2, corner_radius=12)
            bubble.pack(anchor="e", padx=20)

        ctk.CTkLabel(bubble, text=text,
                     font=ctk.CTkFont("Segoe UI", 13),
                     text_color=C_TEXT, justify="left",
                     wraplength=780 if is_ai else 560
                     ).pack(padx=14, pady=(4 if is_ai else 10, 12), anchor="w")

        # Scroll al final
        self.after(50, lambda: self._chat_scroll._parent_canvas.yview_moveto(1.0))

    def _add_typing(self):
        self._typing_msg = ctk.CTkFrame(self._chat_scroll, fg_color="transparent")
        self._typing_msg.pack(fill="x", pady=4)
        ctk.CTkLabel(self._typing_msg,
                     text="Luna está pensando…",
                     font=ctk.CTkFont("Segoe UI", 12, slant="italic"),
                     text_color=C_MUTED
                     ).pack(anchor="w", padx=34)
        self.after(50, lambda: self._chat_scroll._parent_canvas.yview_moveto(1.0))

    # ══════════════════════════════════════════
    #  PÁGINA: ALERTAS
    # ══════════════════════════════════════════
    def _mk_alertas(self):
        pg = ctk.CTkFrame(self._content, fg_color=C_BG)
        pg.grid_columnconfigure(0, weight=1)
        pg.grid_rowconfigure(1, weight=1)

        # Header + filtros
        hdr = ctk.CTkFrame(pg, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=30, pady=(30, 12), sticky="ew")
        ctk.CTkLabel(hdr, text="Gestión de Alertas",
                     font=ctk.CTkFont("Segoe UI", 24, "bold"),
                     text_color=C_TEXT).pack(side="left")

        self._filtro = "Activa"
        self._filtro_btns: dict = {}
        filt_frm = ctk.CTkFrame(hdr, fg_color="transparent")
        filt_frm.pack(side="right")
        for f in ["Activa", "Atendida", "Escalada", "Todas"]:
            b = ctk.CTkButton(filt_frm, text=f, width=82,
                              fg_color=C_ACCENT if f == "Activa" else C_CARD2,
                              hover_color=C_ACCENTHOV,
                              font=ctk.CTkFont("Segoe UI", 12),
                              command=lambda x=f: self._filtrar(x))
            b.pack(side="left", padx=4)
            self._filtro_btns[f] = b

        # Lista de alertas
        self._alert_list = ctk.CTkScrollableFrame(pg, fg_color="transparent")
        self._alert_list.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        return pg

    def _filtrar(self, f: str):
        self._filtro = f
        for k, b in self._filtro_btns.items():
            b.configure(fg_color=C_ACCENT if k == f else C_CARD2)
        self._refresh_alertas()

    def _refresh_alertas(self):
        for w in self._alert_list.winfo_children():
            w.destroy()

        s = get_session()
        try:
            q = s.query(Alerta).order_by(Alerta.fecha.desc())
            if self._filtro != "Todas":
                q = q.filter_by(estado=self._filtro)
            alertas = q.all()

            if not alertas:
                ctk.CTkLabel(self._alert_list,
                             text="No hay alertas en esta categoría.",
                             text_color=C_MUTED,
                             font=ctk.CTkFont("Segoe UI", 14)
                             ).pack(pady=50)
                return

            for a in alertas:
                c = C_RED if a.prioridad == "Alta" else (
                    C_ORANGE if a.prioridad == "Media" else C_GREEN)
                card = ctk.CTkFrame(self._alert_list, fg_color=C_CARD,
                                    corner_radius=10,
                                    border_width=1, border_color=c)
                card.pack(fill="x", pady=7)

                # Top: prioridad + fecha
                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x", padx=16, pady=(12, 4))
                ctk.CTkLabel(top,
                             text=f"  {a.prioridad.upper()}  ",
                             fg_color=c, corner_radius=4,
                             font=ctk.CTkFont("Segoe UI", 10, "bold"),
                             text_color="white").pack(side="left")
                ctk.CTkLabel(top,
                             text=f" · {a.tipo.replace('_', ' ').title()}",
                             font=ctk.CTkFont("Segoe UI", 12, "bold"),
                             text_color=C_TEXT).pack(side="left", padx=6)
                if a.fecha:
                    ctk.CTkLabel(top,
                                 text=a.fecha.strftime("%d/%m/%Y %H:%M"),
                                 text_color=C_MUTED,
                                 font=ctk.CTkFont("Segoe UI", 11)
                                 ).pack(side="right")

                # Estudiante
                est_name = a.estudiante.nombre if a.estudiante else f"#{a.estudiante_id}"
                ctk.CTkLabel(card, text=f"👤  {est_name}",
                             text_color=C_MUTED,
                             font=ctk.CTkFont("Segoe UI", 11)).pack(anchor="w", padx=16)

                # Descripcion
                ctk.CTkLabel(card, text=a.descripcion, justify="left",
                             text_color=C_TEXT, wraplength=900,
                             font=ctk.CTkFont("Segoe UI", 13)
                             ).pack(anchor="w", padx=16, pady=(6, 10))

                # Acciones reactivas basadas en la máquina de estados
                act_frm = ctk.CTkFrame(card, fg_color="transparent")
                act_frm.pack(fill="x", padx=16, pady=(0, 12))
                
                if a.estado == "Activa":
                    ctk.CTkButton(act_frm, text="✔  Marcar Atendida", width=120,
                                  fg_color=C_GREEN, hover_color=C_GREENHOV,
                                  command=lambda aid=a.id: self._set_alerta(aid, "Atendida")
                                  ).pack(side="right", padx=6)
                    ctk.CTkButton(act_frm, text="⬆  Escalar", width=100,
                                  fg_color=C_ORANGE, hover_color="#b45309",
                                  command=lambda aid=a.id: self._set_alerta(aid, "Escalada")
                                  ).pack(side="right", padx=6)
                    ctk.CTkButton(act_frm, text="🗑 Eliminar", width=80,
                                  fg_color="#881337", hover_color="#4c0519", # Red obscuro
                                  command=lambda aid=a.id: self._set_alerta(aid, "Eliminar")
                                  ).pack(side="left")
                elif a.estado == "Escalada":
                    ctk.CTkButton(act_frm, text="✔  Marcar Atendida", width=120,
                                  fg_color=C_GREEN, hover_color=C_GREENHOV,
                                  command=lambda aid=a.id: self._set_alerta(aid, "Atendida")
                                  ).pack(side="right", padx=6)
                    ctk.CTkButton(act_frm, text="⬇  Desescalar", width=100,
                                  fg_color=C_ACCENT, hover_color="#1d4ed8",
                                  command=lambda aid=a.id: self._set_alerta(aid, "Activa")
                                  ).pack(side="right", padx=6)
                    ctk.CTkButton(act_frm, text="🔄  Re-notificar", width=110,
                                  fg_color="#0891b2", hover_color="#164e63", # Cyan
                                  command=lambda aid=a.id: self._set_alerta(aid, "Re-notificar")
                                  ).pack(side="left")
                elif a.estado == "Atendida":
                    ctk.CTkLabel(act_frm,
                                 text=f"Estado Confirmado: {a.estado}",
                                 text_color=C_MUTED,
                                 font=ctk.CTkFont("Segoe UI", 11)
                                 ).pack(side="left", padx=0)
                    ctk.CTkButton(act_frm, text="♻  Reabrir", width=100,
                                  fg_color=C_ACCENT, hover_color="#1d4ed8",
                                  command=lambda aid=a.id: self._set_alerta(aid, "Activa")
                                  ).pack(side="right", padx=6)
                    ctk.CTkButton(act_frm, text="🗑 Eliminar", width=80,
                                  fg_color="#881337", hover_color="#4c0519",
                                  command=lambda aid=a.id: self._set_alerta(aid, "Eliminar")
                                  ).pack(side="right", padx=6)
        finally:
            s.close()

    def _set_alerta(self, aid: int, estado: str):
        s = get_session()
        try:
            a = s.query(Alerta).get(aid)
            if a:
                # Caso Borrado Permanente
                if estado == "Eliminar":
                    s.delete(a)
                    s.commit()
                    self._refresh_alertas()
                    return
                
                # Caso Renotificación / Escalado Inicial a Telegram (Sin salir de estado actual si ya está escalada)
                if estado == "Re-notificar" or estado == "Escalada":
                    from telegram_bot import get_telegram_service
                    tg = get_telegram_service()
                    if a.estudiante and a.estudiante.telegram_chat_id:
                        prefix = "📢 *RECORDATORIO DE COORDINACIÓN (SAE)*" if estado == "Re-notificar" else "⚠️ *MENSAJE OFICIAL COORDINACIÓN (SAE)* ⚠️"
                        msg = (f"{prefix}\n\n"
                               f"Estimado(a) {a.estudiante.nombre}. Se te requiere atención directa por una alerta:\n\n"
                               f"📝 *Motivo:* {a.descripcion}\n"
                               f"📍 *Acción:* Por favor, reportarse con su tutor lo antes posible.\n\n"
                               f"_Responde a Luna si necesitas ayuda._")
                        tg.send_alert(a.estudiante.telegram_chat_id, msg)
                    
                # Siempre actualizar el estado visual excepto si es un mero empuje del recordatorio
                if estado != "Re-notificar":
                    a.estado = estado
                    
                s.commit()
                
            self._refresh_alertas()
        finally:
            s.close()

    # ══════════════════════════════════════════
    #  PÁGINA: REPORTES PDF
    # ══════════════════════════════════════════
    def _mk_reportes(self):
        pg = ctk.CTkFrame(self._content, fg_color=C_BG)
        pg.grid_columnconfigure(0, weight=1)
        pg.grid_rowconfigure(1, weight=1)

        # Header
        ctk.CTkLabel(pg, text="Generación de Reportes PDF",
                     font=ctk.CTkFont("Segoe UI", 24, "bold"),
                     text_color=C_TEXT
                     ).grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")

        # Contenido central
        center = ctk.CTkFrame(pg, fg_color=C_CARD, corner_radius=14,
                              border_width=1, border_color=C_BORDER)
        center.grid(row=1, column=0, padx=80, pady=20, sticky="nsew")
        center.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(center, text="📋",
                     font=ctk.CTkFont(size=52)).grid(row=0, column=0, pady=(40, 10))
        ctk.CTkLabel(center, text="Reporte de Riesgo Académico por Corte",
                     font=ctk.CTkFont("Segoe UI", 18, "bold"),
                     text_color=C_TEXT).grid(row=1, column=0, pady=(0, 8))
        ctk.CTkLabel(center,
                     text="Incluye: Resumen ejecutivo · Estudiantes en riesgo Alto y Medio\n"
                          "Historial de intervenciones · Alertas activas · Estadísticas generales",
                     text_color=C_MUTED,
                     font=ctk.CTkFont("Segoe UI", 13),
                     justify="center").grid(row=2, column=0, pady=(0, 30))

        self._btn_pdf = ctk.CTkButton(center,
                                      text="📥  Generar y Guardar PDF",
                                      width=260, height=48,
                                      fg_color=C_ACCENT, hover_color=C_ACCENTHOV,
                                      font=ctk.CTkFont("Segoe UI", 14, "bold"),
                                      command=self._generar_pdf)
        self._btn_pdf.grid(row=3, column=0, pady=(0, 20))

        self._lbl_pdf_status = ctk.CTkLabel(center, text="",
                                            text_color=C_MUTED,
                                            font=ctk.CTkFont("Segoe UI", 12))
        self._lbl_pdf_status.grid(row=4, column=0, pady=(0, 40))

        # Historial de reportes generados
        ctk.CTkLabel(center, text="Reportes generados anteriormente:",
                     text_color=C_MUTED,
                     font=ctk.CTkFont("Segoe UI", 11)).grid(row=5, column=0, padx=30, sticky="w")

        self._historial_reportes = ctk.CTkScrollableFrame(center, height=120,
                                                           fg_color=C_CARD2,
                                                           corner_radius=8)
        self._historial_reportes.grid(row=6, column=0, padx=30, pady=(4, 30), sticky="ew")
        self._actualizar_historial_reportes()

        return pg

    def _generar_pdf(self):
        from tkinter import filedialog
        from datetime import datetime
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M")
        ruta = filedialog.asksaveasfilename(
            title="Guardar Reporte PDF",
            initialfile=f"reporte_SAE_{fecha_str}.pdf",
            defaultextension=".pdf",
            filetypes=[("Archivo PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        if not ruta:  # Usuario canceló
            return

        self._btn_pdf.configure(state="disabled", text="Generando…")
        self._lbl_pdf_status.configure(text="Procesando datos y construyendo PDF…",
                                       text_color=C_MUTED)

        def _worker():
            try:
                ok, result = generar_reporte_riesgos(output_path=ruta)
                def _ok():
                    self._btn_pdf.configure(state="normal",
                                            text="📥  Generar y Guardar PDF")
                    if ok:
                        self._lbl_pdf_status.configure(
                            text=f"✅  PDF guardado en:\n{result}",
                            text_color=C_GREEN)
                        self._actualizar_historial_reportes()
                        messagebox.showinfo("Reporte generado",
                                            f"El reporte se guardó exitosamente en:\n\n{result}")
                    else:
                        self._lbl_pdf_status.configure(
                            text=f"❌  Error: {result}", text_color=C_RED)
                        messagebox.showerror("Error al generar PDF", str(result))
                self.after(0, _ok)
            except Exception as e:
                self.after(0, lambda: (
                    self._btn_pdf.configure(state="normal",
                                            text="📥  Generar y Guardar PDF"),
                    self._lbl_pdf_status.configure(
                        text=f"❌  Error inesperado: {e}", text_color=C_RED)
                ))

        threading.Thread(target=_worker, daemon=True).start()

    def _actualizar_historial_reportes(self):
        for w in self._historial_reportes.winfo_children():
            w.destroy()
        pdfs = sorted(
            [f for f in os.listdir(_BASE)
             if f.startswith("reporte") and f.endswith(".pdf")],
            reverse=True
        )
        if not pdfs:
            ctk.CTkLabel(self._historial_reportes,
                         text="Aún no hay reportes generados.",
                         text_color=C_MUTED).pack(pady=8)
        for p in pdfs[:10]:
            ctk.CTkLabel(self._historial_reportes,
                         text=f"📄  {p}",
                         text_color=C_TEXT,
                         font=ctk.CTkFont("Segoe UI", 11)).pack(anchor="w", padx=10, pady=3)

    # ══════════════════════════════════════════
    #  PÁGINA: VISIÓN YOLO
    # ══════════════════════════════════════════
    def _mk_vision(self):
        pg = ctk.CTkFrame(self._content, fg_color=C_BG)
        pg.grid_columnconfigure(0, weight=3)
        pg.grid_columnconfigure(1, weight=1)
        pg.grid_rowconfigure(1, weight=1)

        # Header
        hdr = ctk.CTkFrame(pg, fg_color="transparent")
        hdr.grid(row=0, column=0, columnspan=2, padx=30, pady=(24, 12), sticky="ew")
        ctk.CTkLabel(hdr, text="Monitoreo de Atención (YOLO)",
                     font=ctk.CTkFont("Segoe UI", 22, "bold"),
                     text_color=C_TEXT).pack(side="left")
        self._btn_cam = ctk.CTkButton(hdr, text="▶  Iniciar Cámara",
                                      fg_color=C_GREEN, hover_color=C_GREENHOV,
                                      width=160, height=38,
                                      font=ctk.CTkFont("Segoe UI", 13, "bold"),
                                      command=self._yolo_toggle)
        self._btn_cam.pack(side="right")

        # Área de video
        cam_frm = ctk.CTkFrame(pg, fg_color=C_CARD, corner_radius=12)
        cam_frm.grid(row=1, column=0, padx=(30, 10), pady=(0, 30), sticky="nsew")
        cam_frm.grid_rowconfigure(0, weight=1)
        cam_frm.grid_columnconfigure(0, weight=1)

        self._cam_label = ctk.CTkLabel(cam_frm, text="Cámara no iniciada",
                                       font=ctk.CTkFont("Segoe UI", 14),
                                       text_color=C_MUTED)
        self._cam_label.grid(row=0, column=0, sticky="nsew")

        # Panel lateral de análisis
        panel = ctk.CTkFrame(pg, fg_color=C_CARD, corner_radius=12,
                             border_width=1, border_color=C_BORDER)
        panel.grid(row=1, column=1, padx=(0, 30), pady=(0, 30), sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Estado en Tiempo Real",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=C_TEXT).grid(row=0, column=0, pady=(18, 6))

        self._lbl_estado = ctk.CTkLabel(panel, text="⏸  STANDBY",
                                        font=ctk.CTkFont("Segoe UI", 20, "bold"),
                                        text_color=C_MUTED)
        self._lbl_estado.grid(row=1, column=0, pady=10)

        # Barra de inatención
        ctk.CTkLabel(panel, text="Nivel de inatención",
                     text_color=C_MUTED,
                     font=ctk.CTkFont("Segoe UI", 11)).grid(row=2, column=0, padx=16, sticky="w")
        self._prog_aten = ctk.CTkProgressBar(panel, progress_color=C_RED,
                                             fg_color=C_CARD2)
        self._prog_aten.grid(row=3, column=0, padx=16, pady=(4, 16), sticky="ew")
        self._prog_aten.set(0)

        # Separador
        ctk.CTkFrame(panel, height=1, fg_color=C_BORDER).grid(
            row=4, column=0, padx=12, sticky="ew")

        ctk.CTkLabel(panel, text="Registro de Alertas",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=C_TEXT).grid(row=5, column=0, padx=16, pady=(14, 4), sticky="w")

        self._yolo_log = ctk.CTkTextbox(panel, fg_color=C_CARD2,
                                        border_width=0, corner_radius=6,
                                        font=ctk.CTkFont("Consolas", 11),
                                        text_color=C_TEXT)
        self._yolo_log.grid(row=6, column=0, padx=12, pady=(0, 14), sticky="nsew")
        panel.grid_rowconfigure(6, weight=1)

        # Inicializar monitor
        self._vision = VisionMonitor()
        self._vision.on_frame_update  = self._yolo_on_frame
        self._vision.on_state_change  = self._yolo_on_state
        self._vision.on_attention_alert = self._yolo_on_alert

        return pg

    def _yolo_toggle(self):
        if self._vision.running:
            self._vision.stop_camera()
            self._btn_cam.configure(text="▶  Iniciar Cámara",
                                    fg_color=C_GREEN, hover_color=C_GREENHOV)
            self._cam_label.configure(image=None, text="Cámara apagada")
            self._lbl_estado.configure(text="⏸  STANDBY", text_color=C_MUTED)
            self._prog_aten.set(0)
        else:
            self._lbl_estado.configure(text="⏳  Iniciando…", text_color=C_ORANGE)
            self._btn_cam.configure(text="⏹  Detener Cámara",
                                    fg_color=C_RED, hover_color="#9b1c1c")
            self._cam_label.configure(text="")
            self._vision.start_camera(0)

    def _yolo_on_frame(self, frame, dets):
        if not self._vision.running:
            return
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Escala: máximo 800x600
            h, w = rgb.shape[:2]
            scale = min(800 / max(w, 1), 600 / max(h, 1), 1.0)
            nw, nh = int(w * scale), int(h * scale)
            img = Image.fromarray(rgb).resize((nw, nh), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(nw, nh))

            def _up():
                self._cam_label.configure(image=ctk_img)
                self._cam_label.image = ctk_img   # evitar GC
            self.after(0, _up)
        except Exception:
            pass

    def _yolo_on_state(self, state: str, frames_dist: int):
        state_map = {
            "ATENTO":      ("🟢  ATENTO",      C_GREEN),
            "DISTRAIDO":   ("🟡  DISTRAIDO",   C_ORANGE),
            "ALERTA":      ("🔴  ALERTA",       C_RED),
            "SIN_PERSONA": ("⬜  SIN PERSONA",  C_MUTED),
        }
        txt, col = state_map.get(state, ("❓ " + state, C_MUTED))
        pct = min(1.0, frames_dist / float(self._vision.ALERT_THRESHOLD + 1))

        def _up():
            self._lbl_estado.configure(text=txt, text_color=col)
            self._prog_aten.set(pct)
        self.after(0, _up)

    def _yolo_on_alert(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        def _up():
            self._yolo_log.insert("end", f"[{ts}] {msg}\n")
            self._yolo_log.yview_moveto(1.0)
        self.after(0, _up)

    # ══════════════════════════════════════════
    #  CARGA DE IA EN BACKGROUND
    # ══════════════════════════════════════════
    def _load_rag_bg(self):
        def _worker():
            try:
                self._rag = get_chatbot()
                if getattr(self._rag, "ready", False):
                    self._rag_ok = True
                    self.after(0, lambda: self._lbl_ia.configure(
                        text="✅  IA Lista (Ollama)", text_color=C_GREEN))
                else:
                    self.after(0, lambda: self._lbl_ia.configure(
                        text="⚠  IA no disponible", text_color=C_ORANGE))
            except Exception as e:
                self.after(0, lambda: self._lbl_ia.configure(
                    text="❌  Error IA", text_color=C_RED))
                print(f"[GUI] Error cargando IA: {e}")
        threading.Thread(target=_worker, daemon=True).start()


if __name__ == "__main__":
    app = AppWindow()
    app.mainloop()
