"""
SIMULADOR DE DESCARGA DE BATERÍA
Proyecto académico de Cálculo II — Integrales definidas.

Requisitos:
    Python 3.10+
    pip install matplotlib

Ejecutar:
    python simulador_bateria.py

Nota académica:
Los perfiles de corriente son los valores representativos definidos en el
proyecto. El simulador calcula la carga consumida integrando cada función
en el tiempo local del tramo: Q = integral I(u) du.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ---------------------------------------------------------------------------
# MODELO MATEMÁTICO
# I(u) = base + pendiente*u, donde u es el tiempo local del tramo en horas.
# La integral desde 0 hasta x es: Q(x) = base*x + pendiente*x²/2.
# ---------------------------------------------------------------------------

ACTIVIDADES = {
    "Reposo": {
        "categoria": "Sin actividad",
        "base": 50.0, "pendiente": 0.0,
        "descripcion": "Consumo constante de reposo: 50 mA"
    },
    "Spotify": {
        "categoria": "Segundo plano",
        "base": 50.0, "pendiente": 0.0,
        "descripcion": "Reproducción de música: aporte de 50 mA"
    },
    "Llamada": {
        "categoria": "Segundo plano",
        "base": 100.0, "pendiente": 0.0,
        "descripcion": "Llamada: aporte de 100 mA"
    },
    "Navegación web": {
        "categoria": "Primer plano",
        "base": 120.0, "pendiente": 20.0,
        "descripcion": "I(u) = 120 + 20u mA"
    },
    "Redes sociales": {
        "categoria": "Primer plano",
        "base": 150.0, "pendiente": 30.0,
        "descripcion": "I(u) = 150 + 30u mA"
    },
    "Asistente de IA": {
        "categoria": "Primer plano",
        "base": 250.0, "pendiente": 50.0,
        "descripcion": "I(u) = 250 + 50u mA"
    },
    "Streaming": {
        "categoria": "Primer plano",
        "base": 350.0, "pendiente": 40.0,
        "descripcion": "I(u) = 350 + 40u mA"
    },
    "Videojuegos": {
        "categoria": "Primer plano",
        "base": 400.0, "pendiente": 80.0,
        "descripcion": "I(u) = 400 + 80u mA"
    },
}

CATEGORIAS = ["Primer plano", "Ninguna actividad"]
SEGUNDO_PLANO = ["Segundo plano", "Ninguna"]
COLORES = {
    "fondo": "#0b1220",
    "panel": "#121c2e",
    "panel2": "#18253a",
    "borde": "#263750",
    "texto": "#edf4ff",
    "suave": "#9eb0c9",
    "azul": "#58a6ff",
    "verde": "#38d996",
    "amarillo": "#f4c95d",
    "rojo": "#ff647c",
    "grafica": "#78b7ff",
}


def carga_consumida(base, pendiente, horas):
    """Integra I(u)=base+pendiente*u desde u=0 hasta u=horas."""
    horas = max(0.0, horas)
    return base * horas + (pendiente * horas * horas / 2.0)


def corriente_instante(base, pendiente, tiempo_local):
    return base + pendiente * max(0.0, tiempo_local)


def formato_horas(horas):
    """Convierte horas decimales a una presentación h y min."""
    minutos_totales = max(0, int(round(horas * 60)))
    h, m = divmod(minutos_totales, 60)
    return f"{h} h {m:02d} min"


class SimuladorBateria:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de descarga de batería | Cálculo II")
        self.root.geometry("1280x820")
        self.root.minsize(1060, 700)
        self.root.configure(bg=COLORES["fondo"])

        self.tramos = []
        self.simulando = False
        self.tiempo_simulado = 0.0
        self.after_id = None

        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")
        self._configurar_estilos()
        self._construir_interfaz()
        self._actualizar_vistas()

    def _configurar_estilos(self):
        c = COLORES
        self.estilo.configure(
            "TCombobox", fieldbackground=c["panel2"], background=c["panel2"],
            foreground=c["texto"], arrowcolor=c["texto"], padding=7
        )
        self.estilo.map(
            "TCombobox",
            fieldbackground=[("readonly", c["panel2"])],
            foreground=[("readonly", c["texto"])]
        )
        self.estilo.configure(
            "TEntry", fieldbackground=c["panel2"], foreground=c["texto"],
            insertcolor=c["texto"], padding=7
        )
        self.estilo.configure(
            "Treeview", background=c["panel"], fieldbackground=c["panel"],
            foreground=c["texto"], rowheight=29, bordercolor=c["borde"],
            font=("Segoe UI", 9)
        )
        self.estilo.configure(
            "Treeview.Heading", background=c["panel2"],
            foreground=c["suave"], relief="flat",
            font=("Segoe UI", 9, "bold")
        )
        self.estilo.map("Treeview", background=[("selected", "#24466c")])
        self.estilo.configure(
            "Horizontal.TProgressbar", troughcolor=c["panel2"],
            background=c["verde"], bordercolor=c["panel2"],
            lightcolor=c["verde"], darkcolor=c["verde"]
        )

    def _label(self, parent, texto, size=10, color=None, bold=False):
        return tk.Label(
            parent, text=texto, bg=parent.cget("bg"),
            fg=color or COLORES["texto"],
            font=("Segoe UI", size, "bold" if bold else "normal")
        )

    def _boton(self, parent, texto, comando, color=None):
        return tk.Button(
            parent, text=texto, command=comando,
            bg=color or COLORES["azul"], fg="#07111f",
            activebackground="#a7d1ff", activeforeground="#07111f",
            relief="flat", bd=0, padx=12, pady=9,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        )

    def _construir_interfaz(self):
        c = COLORES

        encabezado = tk.Frame(self.root, bg=c["fondo"])
        encabezado.pack(fill="x", padx=22, pady=(17, 10))
       
        tk.Label(
            encabezado, text="Simulador de descarga de batería",
            bg=c["fondo"], fg=c["texto"], font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", pady=(1, 2))
        tk.Label(
            encabezado,
            text="Modelo por tramos · Corriente instantánea e integrales definidas",
            bg=c["fondo"], fg=c["suave"], font=("Segoe UI", 10)
        ).pack(anchor="w")

        principal = tk.Frame(self.root, bg=c["fondo"])
        principal.pack(fill="both", expand=True, padx=22, pady=(0, 20))
        principal.grid_columnconfigure(0, weight=0, minsize=315)
        principal.grid_columnconfigure(1, weight=1)
        principal.grid_rowconfigure(0, weight=1)

        self.panel_izq = tk.Frame(
            principal, bg=c["panel"], highlightbackground=c["borde"],
            highlightthickness=1
        )
        self.panel_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.panel_der = tk.Frame(principal, bg=c["fondo"])
        self.panel_der.grid(row=0, column=1, sticky="nsew")
        self.panel_der.grid_columnconfigure(0, weight=1)
        self.panel_der.grid_rowconfigure(1, weight=1)

        self._construir_controles()
        self._construir_bateria()
        self._construir_graficas()
        self._construir_tabla()
        self._cambiar_categoria()
        self._cambiar_categoria2()

    def _construir_controles(self):
        p = self.panel_izq
        c = COLORES
        tk.Label(
            p, text="CONFIGURAR ACTIVIDAD", bg=c["panel"], fg=c["texto"],
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=16, pady=(16, 12))

        tk.Label(p, text="1. Primer plano", bg=c["panel"], fg=c["suave"],
                 font=("Segoe UI", 9)).pack(anchor="w", padx=16)
        self.categoria_var = tk.StringVar(value="Primer plano")
        self.categoria_combo = ttk.Combobox(
            p, textvariable=self.categoria_var,
            values=["Primer plano", "Ninguna actividad"], state="readonly"
        )
        self.categoria_combo.pack(fill="x", padx=16, pady=(4, 8))
        self.categoria_combo.bind("<<ComboboxSelected>>", self._cambiar_categoria)

        tk.Label(p, text="2. Actividad de primer plano", bg=c["panel"], fg=c["suave"],
                 font=("Segoe UI", 9)).pack(anchor="w", padx=16)
        self.actividad_var = tk.StringVar(value="Navegación web")
        self.actividad_combo = ttk.Combobox(
            p, textvariable=self.actividad_var, state="readonly"
        )
        self.actividad_combo.pack(fill="x", padx=16, pady=(4, 8))
        self.actividad_combo.bind("<<ComboboxSelected>>", self._actualizar_descripcion)

        tk.Label(p, text="3. Segundo plano", bg=c["panel"], fg=c["suave"],
                 font=("Segoe UI", 9)).pack(anchor="w", padx=16)
        self.categoria2_var = tk.StringVar(value="Segundo plano")
        self.categoria2_combo = ttk.Combobox(
            p, textvariable=self.categoria2_var,
            values=["Segundo plano", "Ninguna"], state="readonly"
        )
        self.categoria2_combo.pack(fill="x", padx=16, pady=(4, 8))
        self.categoria2_combo.bind("<<ComboboxSelected>>", self._cambiar_categoria2)

        tk.Label(p, text="4. Actividad de segundo plano", bg=c["panel"], fg=c["suave"],
                 font=("Segoe UI", 9)).pack(anchor="w", padx=16)
        self.actividad2_var = tk.StringVar(value="Spotify")
        self.actividad2_combo = ttk.Combobox(
            p, textvariable=self.actividad2_var, state="readonly",
            values=["Spotify", "Llamada"]
        )
        self.actividad2_combo.pack(fill="x", padx=16, pady=(4, 7))
        self.actividad2_combo.bind("<<ComboboxSelected>>", self._actualizar_descripcion)

        self.descripcion_label = tk.Label(
            p, text="", bg=c["panel"], fg=c["azul"],
            font=("Segoe UI", 9), wraplength=275, justify="left"
        )
        self.descripcion_label.pack(anchor="w", padx=16, pady=(0, 10))

        tk.Label(p, text="Duración del tramo (horas)", bg=c["panel"],
                 fg=c["suave"], font=("Segoe UI", 9)).pack(anchor="w", padx=16)
        self.duracion_var = tk.StringVar(value="0.75")
        ttk.Entry(p, textvariable=self.duracion_var).pack(
            fill="x", padx=16, pady=(4, 12)
        )

        tk.Label(p, text="Capacidad de la batería", bg=c["panel"],
                 fg=c["suave"], font=("Segoe UI", 9)).pack(anchor="w", padx=16)
        self.capacidad_var = tk.StringVar(value="3000")
        self.capacidad_combo = ttk.Entry(
            p, textvariable=self.capacidad_var
        )
        self.capacidad_combo.pack(fill="x", padx=16, pady=(4, 14))
        self.capacidad_combo.bind("<KeyRelease>", lambda e: self._actualizar_vistas())

        self._boton(p, "＋  Agregar tramo", self.agregar_tramo, c["verde"]).pack(
            fill="x", padx=16, pady=(0, 8)
        )
        self._boton(p, "▶  Iniciar simulación", self.iniciar_simulacion).pack(
            fill="x", padx=16, pady=4
        )
        self._boton(p, "Ⅱ  Pausar / reanudar", self.pausar_reanudar, c["amarillo"]).pack(
            fill="x", padx=16, pady=4
        )
        self._boton(p, "↺  Reiniciar simulación", self.reiniciar, "#d2deee").pack(
            fill="x", padx=16, pady=4
        )
        self._boton(p, "Eliminar tramo seleccionado", self.eliminar_tramo, c["panel2"]).pack(
            fill="x", padx=16, pady=4
        )

        tk.Label(
            p,
            text="Modelo académico: Q = ∫ I(u) du\n"
                 "La corriente se expresa en mA y el tiempo en horas; "
                 "la carga consumida se expresa en mAh.",
            bg=c["panel"], fg=c["suave"], font=("Segoe UI", 8),
            wraplength=280, justify="left"
        ).pack(anchor="w", padx=16, pady=(15, 14))

    def _construir_bateria(self):
        c = COLORES
        card = tk.Frame(
            self.panel_der, bg=c["panel"], highlightbackground=c["borde"],
            highlightthickness=1
        )
        card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        card.grid_columnconfigure(1, weight=1)

        tk.Label(card, text="BATERÍA ACTUAL", bg=c["panel"], fg=c["suave"],
                 font=("Segoe UI", 9, "bold")).grid(
                     row=0, column=0, sticky="w", padx=16, pady=(12, 0)
                 )
        self.porcentaje_label = tk.Label(
            card, text="100.0%", bg=c["panel"], fg=c["verde"],
            font=("Segoe UI", 26, "bold")
        )
        self.porcentaje_label.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 5))

        self.bateria_canvas = tk.Canvas(
            card, width=270, height=64, bg=c["panel"],
            highlightthickness=0
        )
        self.bateria_canvas.grid(row=0, column=1, rowspan=2, sticky="e", padx=18, pady=8)

        info = tk.Frame(card, bg=c["panel"])
        info.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(2, 12))
        self.carga_label = tk.Label(info, text="Carga restante: 3000 mAh",
                                    bg=c["panel"], fg=c["texto"],
                                    font=("Segoe UI", 10, "bold"))
        self.carga_label.pack(side="left")
        self.tiempo_label = tk.Label(info, text="Tiempo: 0 h 00 min",
                                    bg=c["panel"], fg=c["suave"],
                                    font=("Segoe UI", 9))
        self.tiempo_label.pack(side="right")

    def _construir_graficas(self):
        c = COLORES
        self.figura = Figure(figsize=(8.0, 4.2), dpi=100, facecolor=c["panel"])
        self.ax_corriente = self.figura.add_subplot(211)
        self.ax_bateria = self.figura.add_subplot(212)
        self.figura.subplots_adjust(left=0.10, right=0.97, top=0.93,
                                    bottom=0.12, hspace=0.52)
        self.canvas_grafica = FigureCanvasTkAgg(self.figura, master=self.panel_der)
        self.canvas_grafica.get_tk_widget().grid(
            row=1, column=0, sticky="nsew", pady=(0, 12)
        )
        self.panel_der.grid_rowconfigure(1, weight=3)

    def _construir_tabla(self):
        c = COLORES
        marco = tk.Frame(
            self.panel_der, bg=c["panel"], highlightbackground=c["borde"],
            highlightthickness=1
        )
        marco.grid(row=2, column=0, sticky="nsew")
        self.panel_der.grid_rowconfigure(2, weight=2)
        tk.Label(
            marco, text="SECUENCIA DE ACTIVIDADES",
            bg=c["panel"], fg=c["texto"], font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=12, pady=(9, 6))

        columnas = ("n", "actividad", "duracion", "funcion", "carga")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=5)
        titulos = {
            "n": "#", "actividad": "Actividad", "duracion": "Duración",
            "funcion": "Función I(u)", "carga": "Carga (mAh)"
        }
        anchos = {"n": 35, "actividad": 185, "duracion": 80, "funcion": 155, "carga": 100}
        for col in columnas:
            self.tabla.heading(col, text=titulos[col])
            self.tabla.column(col, width=anchos[col], anchor="w" if col == "actividad" else "center")
        self.tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _actividades_categoria(self, categoria):
        return [nombre for nombre, datos in ACTIVIDADES.items()
                if datos["categoria"] == categoria]

    def _cambiar_categoria(self, _event=None):
        opciones = self._actividades_categoria("Primer plano")
        if self.categoria_var.get() == "Ninguna actividad":
            self.actividad_var.set("Reposo")
            self.actividad_combo.configure(state="disabled")
        else:
            self.actividad_combo.configure(state="readonly")
            self.actividad_combo["values"] = opciones
            if self.actividad_var.get() not in opciones:
                self.actividad_var.set(opciones[0])
        self._actualizar_descripcion()

    def _cambiar_categoria2(self, _event=None):
        if self.categoria2_var.get() == "Ninguna":
            self.actividad2_var.set("Ninguna")
            self.actividad2_combo.configure(state="disabled")
        else:
            self.actividad2_combo.configure(state="readonly")
            self.actividad2_combo["values"] = ["Spotify", "Llamada"]
            if self.actividad2_var.get() not in ("Spotify", "Llamada"):
                self.actividad2_var.set("Spotify")
        self._actualizar_descripcion()

    def _actualizar_descripcion(self, _event=None):
        nombres = []
        if self.categoria_var.get() == "Primer plano":
            nombres.append(self.actividad_var.get())
        if self.categoria2_var.get() == "Segundo plano":
            nombres.append(self.actividad2_var.get())
        if not nombres:
            nombres = ["Reposo"]
        detalles = []
        for nombre in nombres:
            if nombre in ACTIVIDADES:
                detalles.append(ACTIVIDADES[nombre]["descripcion"])
        self.descripcion_label.config(text=" + ".join(detalles))

    def agregar_tramo(self):
        primer_plano = (self.actividad_var.get()
                        if self.categoria_var.get() == "Primer plano" else None)
        segundo_plano = (self.actividad2_var.get()
                         if self.categoria2_var.get() == "Segundo plano" else None)

        try:
            duracion = float(self.duracion_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Duración no válida", "Escribe una duración numérica, por ejemplo 0.75.")
            return
        if not math.isfinite(duracion) or duracion <= 0 or duracion > 24:
            messagebox.showerror("Duración no válida", "La duración debe ser mayor que 0 y no superar 24 horas.")
            return

        try:
            capacidad = float(self.capacidad_var.get().replace(",", "."))
            if not math.isfinite(capacidad) or capacidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Capacidad no válida", "Ingresa una capacidad de batería mayor que 0 mAh.")
            return

        nombres = []
        base = 0.0
        pendiente = 0.0

        if primer_plano:
            datos = ACTIVIDADES[primer_plano]
            base += datos["base"]
            pendiente += datos["pendiente"]
            nombres.append(primer_plano)

        if segundo_plano:
            datos = ACTIVIDADES[segundo_plano]
            # El consumo de segundo plano se suma al primer plano.
            # Si no hay primer plano, se usa como consumo único.
            if primer_plano:
                base += datos["base"]
            else:
                base = datos["base"]
            nombres.append("Música" if segundo_plano == "Spotify" else segundo_plano)

        if not nombres:
            nombres = ["Reposo"]
            base = ACTIVIDADES["Reposo"]["base"]

        nombre = " + ".join(nombres)
        tramo = {
            "nombre": nombre,
            "categoria": "Combinada" if len(nombres) > 1 else (
                "Primer plano" if primer_plano else "Segundo plano" if segundo_plano else "Sin actividad"
            ),
            "base": base, "pendiente": pendiente, "duracion": duracion
        }
        self.tramos.append(tramo)
        self._actualizar_vistas()

    def eliminar_tramo(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Selecciona un tramo", "Selecciona una fila de la secuencia para eliminarla.")
            return
        indice = self.tabla.index(seleccion[0])
        if 0 <= indice < len(self.tramos):
            del self.tramos[indice]
            self.reiniciar(mostrar_mensaje=False)

    def reiniciar(self, mostrar_mensaje=False):
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
        self.after_id = None
        self.simulando = False
        self.tiempo_simulado = 0.0
        self._actualizar_vistas()
        if mostrar_mensaje:
            messagebox.showinfo("Simulación reiniciada", "Se ha reiniciado el avance de la simulación.")

    def pausar_reanudar(self):
        if not self.tramos:
            messagebox.showinfo("Sin actividades", "Agrega uno o más tramos antes de simular.")
            return
        if self.simulando:
            self.simulando = False
            if self.after_id is not None:
                try:
                    self.root.after_cancel(self.after_id)
                except tk.TclError:
                    pass
                self.after_id = None
        else:
            self.simulando = True
            self._paso_simulacion()

    def iniciar_simulacion(self):
        if not self.tramos:
            messagebox.showinfo("Sin actividades", "Primero agrega al menos un tramo a la secuencia.")
            return
        self.reiniciar()
        self.simulando = True
        self._paso_simulacion()

    def _paso_simulacion(self):
        if not self.simulando:
            return
        total = sum(t["duracion"] for t in self.tramos)
        if self.tiempo_simulado >= total:
            self.tiempo_simulado = total
            self.simulando = False
            self.after_id = None
            self._actualizar_vistas()
            return
        # Avance virtual: 0.015 h cada 80 ms (aprox. 45 s reales por hora simulada).
        self.tiempo_simulado = min(total, self.tiempo_simulado + 0.015)
        self._actualizar_vistas()
        self.after_id = self.root.after(80, self._paso_simulacion)

    def _capacidad(self):
        try:
            valor = float(self.capacidad_var.get().replace(",", "."))
            return valor if math.isfinite(valor) and valor > 0 else 3000.0
        except ValueError:
            return 3000.0

    def _consumo_hasta(self, tiempo):
        consumido = 0.0
        restante = max(0.0, tiempo)
        for tramo in self.tramos:
            dt = min(tramo["duracion"], restante)
            if dt > 0:
                consumido += carga_consumida(tramo["base"], tramo["pendiente"], dt)
                restante -= dt
            if restante <= 0:
                break
        return consumido

    def _datos_graficas(self):
        # Puntos de la curva, con muestreo fino por tramo y continuidad del tiempo global.
        tiempos = [0.0]
        corrientes = []
        tiempos_bat = [0.0]
        porcentajes = [100.0]
        t_global = 0.0
        carga = 0.0

        for tramo in self.tramos:
            pasos = max(12, int(tramo["duracion"] * 35))
            for i in range(1, pasos + 1):
                u = tramo["duracion"] * i / pasos
                tg = t_global + u
                q = carga + carga_consumida(tramo["base"], tramo["pendiente"], u)
                tiempos.append(tg)
                corrientes.append(corriente_instante(tramo["base"], tramo["pendiente"], u))
                tiempos_bat.append(tg)
                porcentajes.append(max(0.0, 100.0 * (self._capacidad() - q) / self._capacidad()))
            carga += carga_consumida(tramo["base"], tramo["pendiente"], tramo["duracion"])
            t_global += tramo["duracion"]

        # Incluir un valor de corriente en el origen para que la gráfica sea legible.
        if self.tramos:
            corrientes.insert(0, self.tramos[0]["base"])
        else:
            tiempos = [0.0, 1.0]
            corrientes = [50.0, 50.0]
            tiempos_bat = [0.0, 1.0]
            porcentajes = [100.0, max(0.0, 100.0 * (self._capacidad() - 50) / self._capacidad())]

        return tiempos, corrientes, tiempos_bat, porcentajes

    def _dibujar_bateria(self, porcentaje):
        c = COLORES
        cv = self.bateria_canvas
        cv.delete("all")
        x0, y0, x1, y1 = 15, 16, 235, 52
        cv.create_rectangle(x0, y0, x1, y1, outline=c["suave"], width=2)
        cv.create_rectangle(x1, 26, x1 + 9, 42, fill=c["suave"], outline=c["suave"])
        pct = max(0.0, min(100.0, porcentaje))
        ancho = (x1 - x0 - 6) * pct / 100.0
        if pct > 0:
            color = c["verde"] if pct > 35 else (c["amarillo"] if pct > 15 else c["rojo"])
            cv.create_rectangle(x0 + 3, y0 + 3, x0 + 3 + ancho, y1 - 3,
                                fill=color, outline=color)
        cv.create_text(260, 34, text=f"{pct:.0f}%", fill=c["texto"],
                       font=("Segoe UI", 10, "bold"), anchor="e")

    def _actualizar_vistas(self):
        capacidad = self._capacidad()
        total_horas = sum(t["duracion"] for t in self.tramos)
        tiempo = min(self.tiempo_simulado, total_horas)
        carga_consumida_total = self._consumo_hasta(tiempo)
        carga_restante = max(0.0, capacidad - carga_consumida_total)
        porcentaje = max(0.0, min(100.0, 100.0 * carga_restante / capacidad))

        color_pct = COLORES["verde"] if porcentaje > 35 else (
            COLORES["amarillo"] if porcentaje > 15 else COLORES["rojo"]
        )
        self.porcentaje_label.config(text=f"{porcentaje:.1f}%", fg=color_pct)
        self.carga_label.config(text=f"Carga restante: {carga_restante:,.2f} mAh")
        self.tiempo_label.config(text=f"Tiempo: {formato_horas(tiempo)}")
        self._dibujar_bateria(porcentaje)

        for item in self.tabla.get_children():
            self.tabla.delete(item)
        acumulado = 0.0
        for i, tramo in enumerate(self.tramos, start=1):
            q = carga_consumida(tramo["base"], tramo["pendiente"], tramo["duracion"])
            acumulado += q
            funcion = f"{tramo['base']:g} + {tramo['pendiente']:g}u"
            self.tabla.insert("", "end", values=(
                i, tramo["nombre"], f"{tramo['duracion']:g} h",
                f"I(u) = {funcion}", f"{q:,.2f}"
            ))

        self._actualizar_graficas(tiempo, porcentaje)

    def _actualizar_graficas(self, tiempo, porcentaje):
        c = COLORES
        for ax in (self.ax_corriente, self.ax_bateria):
            ax.clear()
            ax.set_facecolor(c["panel"])
            ax.tick_params(colors=c["suave"], labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(c["borde"])
            ax.grid(True, color=c["borde"], alpha=0.7, linewidth=0.7)

        tiempos, corrientes, tiempos_bat, porcentajes = self._datos_graficas()

        self.ax_corriente.plot(tiempos, corrientes, color=c["azul"], linewidth=2.2)
        self.ax_corriente.fill_between(tiempos, corrientes, color=c["azul"], alpha=0.12)
        self.ax_corriente.set_title("Corriente instantánea por actividad", color=c["texto"],
                                    fontsize=10, fontweight="bold", loc="left", pad=7)
        self.ax_corriente.set_ylabel("Corriente (mA)", color=c["suave"], fontsize=8)
        self.ax_corriente.set_xlim(left=0)
        if tiempos and len(tiempos) > 1:
            self.ax_corriente.set_xlim(0, max(tiempos[-1], 0.5))
        # Etiquetar cada tramo en el centro de su curva de corriente.
        t_inicio = 0.0
        for tramo in self.tramos:
            t_centro = t_inicio + tramo["duracion"] / 2
            u_centro = tramo["duracion"] / 2
            i_centro = corriente_instante(tramo["base"], tramo["pendiente"], u_centro)
            self.ax_corriente.annotate(
                tramo["nombre"], (t_centro, i_centro),
                xytext=(0, 9), textcoords="offset points",
                ha="center", va="bottom", fontsize=7, color=c["texto"],
                bbox=dict(boxstyle="round,pad=0.2", fc=c["panel"], ec=c["borde"], alpha=0.9)
            )
            t_inicio += tramo["duracion"]

        self.ax_bateria.plot(tiempos_bat, porcentajes, color=c["verde"], linewidth=2.4)
        self.ax_bateria.fill_between(tiempos_bat, porcentajes, color=c["verde"], alpha=0.12)
        self.ax_bateria.set_title("Porcentaje estimado de batería", color=c["texto"],
                                  fontsize=10, fontweight="bold", loc="left", pad=7)
        self.ax_bateria.set_xlabel("Tiempo transcurrido (horas)", color=c["suave"], fontsize=8)
        self.ax_bateria.set_ylabel("Batería (%)", color=c["suave"], fontsize=8)
        self.ax_bateria.set_ylim(0, 105)
        self.ax_bateria.set_xlim(0, max(tiempos_bat[-1] if tiempos_bat else 1, 0.5))
        # Etiquetar también cada descenso de batería con la actividad correspondiente.
        t_inicio = 0.0
        carga_previa = 0.0
        capacidad = self._capacidad()
        for tramo in self.tramos:
            t_centro = t_inicio + tramo["duracion"] / 2
            carga_media = carga_previa + carga_consumida(
                tramo["base"], tramo["pendiente"], tramo["duracion"] / 2
            )
            pct_centro = max(0.0, 100.0 * (capacidad - carga_media) / capacidad)
            self.ax_bateria.annotate(
                tramo["nombre"], (t_centro, pct_centro),
                xytext=(0, -15), textcoords="offset points",
                ha="center", va="top", fontsize=7, color=c["texto"],
                bbox=dict(boxstyle="round,pad=0.2", fc=c["panel"], ec=c["borde"], alpha=0.9)
            )
            carga_previa += carga_consumida(tramo["base"], tramo["pendiente"], tramo["duracion"])
            t_inicio += tramo["duracion"]

        if self.tramos:
            # Marcador del tiempo simulado sobre la curva de batería.
            self.ax_bateria.axvline(tiempo, color=c["amarillo"], linestyle="--", linewidth=1.2)
            self.ax_bateria.scatter([tiempo], [porcentaje], color=c["amarillo"], s=35, zorder=5)
        self.figura.tight_layout(pad=1.7)
        self.canvas_grafica.draw_idle()


def main():
    root = tk.Tk()
    app = SimuladorBateria(root)
    root.mainloop()


if __name__ == "__main__":
    main()
