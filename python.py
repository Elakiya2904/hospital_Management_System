import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import time
import threading

# ─────────────────────────────────────────
#  THEME CONSTANTS
# ─────────────────────────────────────────
BG          = "#0D1117"
PANEL       = "#161B22"
CARD        = "#1C2333"
BORDER      = "#30363D"
ACCENT      = "#2FA8E0"
ACCENT2     = "#1A7EAA"
SUCCESS     = "#3FB950"
WARNING     = "#D29922"
DANGER      = "#F85149"
TEXT        = "#E6EDF3"
TEXT_MID    = "#8B949E"
TEXT_DIM    = "#484F58"
WHITE       = "#FFFFFF"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_SUB    = ("Segoe UI", 11)
FONT_LABEL  = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI", 10, "bold")
FONT_SMALL  = ("Segoe UI", 9)
FONT_NAV    = ("Segoe UI", 10, "bold")
FONT_BIG    = ("Segoe UI", 28, "bold")
FONT_MED    = ("Segoe UI", 14, "bold")


# ─────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="system",
            database="hospital_management"
        )
        return conn
    except Exception:
        return None


# ─────────────────────────────────────────
#  CUSTOM WIDGETS
# ─────────────────────────────────────────
class RoundedButton(tk.Canvas):
    """Fully custom rounded button with hover animation."""

    def __init__(self, parent, text, command=None, width=200, height=42,
                 bg=ACCENT, fg=WHITE, hover_bg=None, radius=10,
                 font=FONT_BOLD, icon=None, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"] if hasattr(parent, "__getitem__") else BG,
                         highlightthickness=0, **kwargs)
        self.command   = command
        self.bg_color  = bg
        self.hover_bg  = hover_bg or self._darken(bg)
        self.fg_color  = fg
        self.radius    = radius
        self.txt       = (icon + "  " + text) if icon else text
        self.font      = font
        self._current  = bg
        self._draw(bg)
        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _darken(self, hex_color):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        factor = 0.80
        return "#{:02x}{:02x}{:02x}".format(int(r*factor), int(g*factor), int(b*factor))

    def _draw(self, bg):
        self.delete("all")
        w, h, r = self.winfo_reqwidth(), self.winfo_reqheight(), self.radius
        self._round_rect(2, 2, w-2, h-2, r, fill=bg, outline="")
        self.create_text(w//2, h//2, text=self.txt, fill=self.fg_color,
                         font=self.font, anchor="center")

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
               x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
               x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        self.create_polygon(pts, smooth=True, **kw)

    def _on_enter(self, _):
        self._draw(self.hover_bg)
        self.config(cursor="hand2")

    def _on_leave(self, _):
        self._draw(self.bg_color)
        self.config(cursor="")

    def _on_click(self, _):
        if self.command:
            self.command()


class FloatingEntry(tk.Frame):
    """Entry with floating label and bottom-border focus style."""

    def __init__(self, parent, label, show=None, **kwargs):
        super().__init__(parent, bg=CARD, **kwargs)
        self.show = show

        self.lbl_var = tk.StringVar(value=label)
        self.label_widget = tk.Label(self, textvariable=self.lbl_var,
                                     bg=CARD, fg=TEXT_DIM, font=FONT_SMALL)
        self.label_widget.pack(anchor="w", padx=2)

        self.entry = tk.Entry(self, bg=PANEL, fg=TEXT, insertbackground=ACCENT,
                              relief="flat", font=FONT_SUB, show=show or "",
                              highlightthickness=0, bd=0)
        self.entry.pack(fill="x", padx=2, pady=(0, 2))

        self.line = tk.Frame(self, bg=BORDER, height=2)
        self.line.pack(fill="x")

        self.entry.bind("<FocusIn>",  self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)

    def _focus_in(self, _):
        self.line.config(bg=ACCENT)
        self.label_widget.config(fg=ACCENT)

    def _focus_out(self, _):
        self.line.config(bg=BORDER)
        self.label_widget.config(fg=TEXT_DIM)

    def get(self):
        return self.entry.get()


class StatCard(tk.Frame):
    """A compact metric card for the dashboard."""

    def __init__(self, parent, icon, value, label, color=ACCENT, **kwargs):
        super().__init__(parent, bg=CARD, bd=0, highlightbackground=BORDER,
                         highlightthickness=1, **kwargs)
        self.columnconfigure(0, weight=1)

        tk.Label(self, text=icon, bg=CARD, fg=color,
                 font=("Segoe UI Emoji", 20)).grid(row=0, column=0, pady=(14, 2))
        tk.Label(self, text=value, bg=CARD, fg=color,
                 font=FONT_BIG).grid(row=1, column=0)
        tk.Label(self, text=label, bg=CARD, fg=TEXT_MID,
                 font=FONT_SMALL).grid(row=2, column=0, pady=(0, 14))


class NavButton(tk.Frame):
    """Sidebar navigation button with active-state indicator."""

    def __init__(self, parent, icon, text, command=None, active=False, **kwargs):
        super().__init__(parent, bg=PANEL, cursor="hand2", **kwargs)
        self.command = command
        self.active  = active
        self.icon_t  = icon
        self.text_t  = text

        self.indicator = tk.Frame(self, bg=ACCENT if active else PANEL, width=3)
        self.indicator.pack(side="left", fill="y")

        inner = tk.Frame(self, bg=CARD if active else PANEL, padx=14, pady=10)
        inner.pack(fill="both", expand=True)
        self.inner = inner

        self.icon_lbl = tk.Label(inner, text=icon, bg=inner["bg"], fg=ACCENT if active else TEXT_MID,
                                 font=("Segoe UI Emoji", 14))
        self.icon_lbl.pack(side="left", padx=(0, 10))
        self.lbl = tk.Label(inner, text=text, bg=inner["bg"],
                            fg=TEXT if active else TEXT_MID, font=FONT_NAV)
        self.lbl.pack(side="left")

        for w in [self, inner, self.icon_lbl, self.lbl]:
            w.bind("<Button-1>", self._click)
        inner.children.get("!label", None)

        self.bind("<Enter>", self._hover)
        self.bind("<Leave>", self._leave)
        inner.bind("<Enter>", self._hover)
        inner.bind("<Leave>", self._leave)

    def _hover(self, _):
        if not self.active:
            self.inner.config(bg=BORDER)
            self.icon_lbl.config(bg=BORDER)
            self.lbl.config(bg=BORDER)

    def _leave(self, _):
        if not self.active:
            self.inner.config(bg=PANEL)
            self.icon_lbl.config(bg=PANEL)
            self.lbl.config(bg=PANEL)

    def _click(self, _):
        if self.command:
            self.command()

    def set_active(self, val):
        self.active = val
        col = CARD if val else PANEL
        self.indicator.config(bg=ACCENT if val else PANEL)
        self.inner.config(bg=col)
        self.icon_lbl.config(bg=col, fg=ACCENT if val else TEXT_MID)
        self.lbl.config(bg=col, fg=TEXT if val else TEXT_MID)


# ─────────────────────────────────────────
#  LOGIN WINDOW
# ─────────────────────────────────────────
class LoginWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hospital Management System — Login")
        self.root.geometry("880x560")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self._center()
        self._build()

    def _center(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - 880) // 2
        y = (self.root.winfo_screenheight() - 560) // 2
        self.root.geometry(f"880x560+{x}+{y}")

    def _build(self):
        # ── Left decorative panel ──
        left = tk.Frame(self.root, bg=ACCENT2, width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="🏥", bg=ACCENT2,
                 font=("Segoe UI Emoji", 52)).pack(pady=(80, 10))
        tk.Label(left, text="MedCare\nHospital", bg=ACCENT2, fg=WHITE,
                 font=("Segoe UI", 28, "bold"), justify="center").pack()
        tk.Label(left, text="Management System", bg=ACCENT2,
                 fg="#cce8f4", font=FONT_SUB).pack(pady=(4, 30))

        # decorative dots
        dots = tk.Frame(left, bg=ACCENT2)
        dots.pack()
        for i, col in enumerate(["#FFFFFF", "#cce8f4", "#8ab8cc"]):
            tk.Label(dots, text="●", bg=ACCENT2, fg=col,
                     font=("Segoe UI", 10)).pack(side="left", padx=4)

        tk.Label(left, text="Secure · Efficient · Reliable",
                 bg=ACCENT2, fg="#cce8f4", font=FONT_SMALL).pack(pady=(20, 0))

        # ── Right login panel ──
        right = tk.Frame(self.root, bg=BG)
        right.pack(side="right", fill="both", expand=True)

        form = tk.Frame(right, bg=BG)
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(form, text="Welcome back", bg=BG, fg=TEXT_MID,
                 font=FONT_SUB).pack(anchor="w")
        tk.Label(form, text="Sign in to continue", bg=BG, fg=TEXT,
                 font=FONT_TITLE).pack(anchor="w", pady=(2, 30))

        # Email field
        self.email_entry = FloatingEntry(form, "Email address", width=320)
        self.email_entry.pack(fill="x", pady=(0, 18))

        # Password field
        self.pass_entry = FloatingEntry(form, "Password", show="*", width=320)
        self.pass_entry.pack(fill="x", pady=(0, 8))

        # Forgot password
        tk.Label(form, text="Forgot password?", bg=BG, fg=ACCENT,
                 font=FONT_SMALL, cursor="hand2").pack(anchor="e", pady=(0, 24))

        # Login button
        RoundedButton(form, "Sign In", command=self._login,
                      width=320, height=44, bg=ACCENT,
                      font=("Segoe UI", 11, "bold")).pack()

        # Status label
        self.status = tk.Label(form, text="", bg=BG, fg=DANGER, font=FONT_SMALL)
        self.status.pack(pady=(12, 0))

        # Version
        tk.Label(right, text="v2.0  ·  MedCare HMS", bg=BG, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side="bottom", pady=12)

        # Bind Enter key
        self.root.bind("<Return>", lambda _: self._login())

    def _login(self):
        email = self.email_entry.get().strip()
        pwd   = self.pass_entry.get().strip()

        if not email or not pwd:
            self.status.config(text="⚠  Please fill in all fields.")
            return

        conn = get_connection()
        if conn is None:
            # Demo mode — accept any login
            self._open_dashboard(email)
            return

        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM users WHERE email=%s AND password=%s",
                (email, pwd)
            )
            user = cur.fetchone()
            conn.close()
            if not user:
                self.status.config(text="✗  Invalid email or password.")
                return

            self._open_dashboard(email)
        except Exception as e:
            if self.status.winfo_exists():
                self.status.config(text=f"✗  Error: {e}")
            else:
                messagebox.showerror("Error", str(e))

    def _open_dashboard(self, user):
        self.root.destroy()
        try:
            DashboardWindow(user).run()
        except KeyboardInterrupt:
            pass

    def run(self):
        self.root.mainloop()


# ─────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────
class DashboardWindow:

    PAGES = ["Dashboard", "Doctors", "Patients", "Appointments", "Payments"]
    ICONS = ["🏠", "👨‍⚕️", "🧑‍🤝‍🧑", "📅", "💳"]

    def __init__(self, user="admin"):
        self.user = user
        self.root = tk.Tk()
        self.root.title("Hospital Management System")
        self.root.geometry("1100x680")
        self.root.configure(bg=BG)
        self._center()
        self.current_page = "Dashboard"
        self.nav_btns = {}
        self._build()

    def _center(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - 1100) // 2
        y = (self.root.winfo_screenheight() - 680)  // 2
        self.root.geometry(f"1100x680+{x}+{y}")

    def _build(self):
        # ── Top bar ──
        topbar = tk.Frame(self.root, bg=PANEL, height=56, bd=0,
                          highlightbackground=BORDER, highlightthickness=1)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="🏥  MedCare HMS", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=20)

        # user info right side
        right_top = tk.Frame(topbar, bg=PANEL)
        right_top.pack(side="right", padx=20)

        tk.Label(right_top, text="●", bg=PANEL, fg=SUCCESS, font=FONT_SMALL).pack(side="left")
        tk.Label(right_top, text=f"  {self.user}", bg=PANEL, fg=TEXT_MID,
                 font=FONT_SMALL).pack(side="left", padx=(2, 14))
        RoundedButton(right_top, "Logout", command=self._logout,
                      width=80, height=30, bg=DANGER, font=FONT_SMALL, radius=8
                      ).pack(side="left")

        # ── Body ──
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(body, bg=PANEL, width=200,
                           highlightbackground=BORDER, highlightthickness=1)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="NAVIGATION", bg=PANEL, fg=TEXT_DIM,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(18, 8))

        for icon, name in zip(self.ICONS, self.PAGES):
            btn = NavButton(sidebar, icon, name,
                            command=lambda n=name: self._switch_page(n),
                            active=(name == "Dashboard"))
            btn.pack(fill="x")
            self.nav_btns[name] = btn

        # bottom of sidebar
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", side="bottom", pady=10)
        tk.Label(sidebar, text="v2.0  MedCare", bg=PANEL, fg=TEXT_DIM,
                 font=("Segoe UI", 8)).pack(side="bottom", pady=(0, 6))

        # Content area
        self.content = tk.Frame(body, bg=BG)
        self.content.pack(fill="both", expand=True)

        self._show_dashboard()

    def _notify(self, title, message):
        messagebox.showinfo(title, message)

    def _db_fetch(self, query, params=None):
        conn = get_connection()
        if conn is None:
            return None
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            conn.close()
            messagebox.showerror("Database Error", str(e))
            return None

    def _db_execute(self, query, params):
        conn = get_connection()
        if conn is None:
            messagebox.showerror("Database Error", "Could not connect to database.")
            return False
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            messagebox.showerror("Database Error", str(e))
            return False

    def _reload_current_page(self):
        for w in self.content.winfo_children():
            w.destroy()
        pages = {
            "Dashboard": self._show_dashboard,
            "Doctors": self._show_doctors,
            "Patients": self._show_patients,
            "Appointments": self._show_appointments,
            "Payments": self._show_payments,
        }
        pages.get(self.current_page, self._show_dashboard)()

    def _open_add_doctor_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Doctor")
        win.geometry("380x280")
        win.configure(bg=BG)
        win.grab_set()

        tk.Label(win, text="Add Doctor", bg=BG, fg=TEXT, font=FONT_MED).pack(pady=(16, 10))

        form = tk.Frame(win, bg=BG)
        form.pack(fill="x", padx=20)

        tk.Label(form, text="Name", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        name_entry = tk.Entry(form, bg=PANEL, fg=TEXT, insertbackground=ACCENT, relief="flat")
        name_entry.pack(fill="x", pady=(0, 10), ipady=6)

        tk.Label(form, text="Specialization", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        spec_entry = tk.Entry(form, bg=PANEL, fg=TEXT, insertbackground=ACCENT, relief="flat")
        spec_entry.pack(fill="x", pady=(0, 10), ipady=6)

        tk.Label(form, text="Phone", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        phone_entry = tk.Entry(form, bg=PANEL, fg=TEXT, insertbackground=ACCENT, relief="flat")
        phone_entry.pack(fill="x", pady=(0, 16), ipady=6)

        def submit():
            name = name_entry.get().strip()
            specialization = spec_entry.get().strip()
            phone = phone_entry.get().strip()
            if not name or not specialization or not phone:
                messagebox.showwarning("Validation", "All fields are required.")
                return

            ok = self._db_execute(
                "INSERT INTO doctors (name, specialization, phone) VALUES (%s, %s, %s)",
                (name, specialization, phone)
            )
            if ok:
                win.destroy()
                self._notify("Doctors", "Doctor added successfully.")
                self.current_page = "Doctors"
                self._reload_current_page()

        RoundedButton(win, "Save Doctor", command=submit, width=150, height=36, bg=ACCENT,
                      font=("Segoe UI", 9, "bold")).pack(pady=4)

    def _open_add_patient_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Register Patient")
        win.geometry("380x340")
        win.configure(bg=BG)
        win.grab_set()

        tk.Label(win, text="Register Patient", bg=BG, fg=TEXT, font=FONT_MED).pack(pady=(16, 10))

        form = tk.Frame(win, bg=BG)
        form.pack(fill="x", padx=20)

        tk.Label(form, text="Name", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        name_entry = tk.Entry(form, bg=PANEL, fg=TEXT, insertbackground=ACCENT, relief="flat")
        name_entry.pack(fill="x", pady=(0, 10), ipady=6)

        tk.Label(form, text="Age", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        age_entry = tk.Entry(form, bg=PANEL, fg=TEXT, insertbackground=ACCENT, relief="flat")
        age_entry.pack(fill="x", pady=(0, 10), ipady=6)

        tk.Label(form, text="Gender", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        gender_combo = ttk.Combobox(form, values=["Male", "Female", "Other"], state="readonly")
        gender_combo.pack(fill="x", pady=(0, 10), ipady=3)
        gender_combo.set("Male")

        tk.Label(form, text="Phone", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        phone_entry = tk.Entry(form, bg=PANEL, fg=TEXT, insertbackground=ACCENT, relief="flat")
        phone_entry.pack(fill="x", pady=(0, 16), ipady=6)

        def submit():
            name = name_entry.get().strip()
            age_text = age_entry.get().strip()
            gender = gender_combo.get().strip()
            phone = phone_entry.get().strip()

            if not name or not age_text or not gender or not phone:
                messagebox.showwarning("Validation", "All fields are required.")
                return
            if not age_text.isdigit():
                messagebox.showwarning("Validation", "Age must be a number.")
                return

            ok = self._db_execute(
                "INSERT INTO patients (name, age, gender, phone) VALUES (%s, %s, %s, %s)",
                (name, int(age_text), gender, phone)
            )
            if ok:
                win.destroy()
                self._notify("Patients", "Patient registered successfully.")
                self.current_page = "Patients"
                self._reload_current_page()

        RoundedButton(win, "Save Patient", command=submit, width=150, height=36, bg=SUCCESS,
                      font=("Segoe UI", 9, "bold")).pack(pady=4)

    def _open_book_appointment_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Book Appointment")
        win.geometry("420x340")
        win.configure(bg=BG)
        win.grab_set()

        tk.Label(win, text="Book Appointment", bg=BG, fg=TEXT, font=FONT_MED).pack(pady=(16, 10))

        patients = self._db_fetch("SELECT patient_id, name FROM patients ORDER BY name")
        doctors = self._db_fetch("SELECT doctor_id, name FROM doctors ORDER BY name")

        if not patients or not doctors:
            messagebox.showwarning("Missing Data", "Add at least one patient and one doctor first.")
            win.destroy()
            return

        patient_options = [f"{pid} - {name}" for pid, name in patients]
        doctor_options = [f"{did} - {name}" for did, name in doctors]

        form = tk.Frame(win, bg=BG)
        form.pack(fill="x", padx=20)

        tk.Label(form, text="Patient", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        patient_combo = ttk.Combobox(form, values=patient_options, state="readonly")
        patient_combo.pack(fill="x", pady=(0, 10), ipady=3)
        patient_combo.set(patient_options[0])

        tk.Label(form, text="Doctor", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        doctor_combo = ttk.Combobox(form, values=doctor_options, state="readonly")
        doctor_combo.pack(fill="x", pady=(0, 10), ipady=3)
        doctor_combo.set(doctor_options[0])

        tk.Label(form, text="Appointment Date (YYYY-MM-DD)", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        date_entry = tk.Entry(form, bg=PANEL, fg=TEXT, insertbackground=ACCENT, relief="flat")
        date_entry.pack(fill="x", pady=(0, 10), ipady=6)

        tk.Label(form, text="Status", bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        status_combo = ttk.Combobox(form, values=["Scheduled", "Completed", "Cancelled"], state="readonly")
        status_combo.pack(fill="x", pady=(0, 16), ipady=3)
        status_combo.set("Scheduled")

        def submit():
            patient_text = patient_combo.get().strip()
            doctor_text = doctor_combo.get().strip()
            appointment_date = date_entry.get().strip()
            status = status_combo.get().strip()

            if not patient_text or not doctor_text or not appointment_date or not status:
                messagebox.showwarning("Validation", "All fields are required.")
                return

            try:
                patient_id = int(patient_text.split(" - ")[0])
                doctor_id = int(doctor_text.split(" - ")[0])
            except Exception:
                messagebox.showwarning("Validation", "Invalid patient/doctor selection.")
                return

            ok = self._db_execute(
                "INSERT INTO appointments (patient_id, doctor_id, appointment_date, status) VALUES (%s, %s, %s, %s)",
                (patient_id, doctor_id, appointment_date, status)
            )
            if ok:
                win.destroy()
                self._notify("Appointments", "Appointment booked successfully.")
                self.current_page = "Appointments"
                self._reload_current_page()

        RoundedButton(win, "Save Appointment", command=submit, width=170, height=36, bg=WARNING,
                      fg=BG, font=("Segoe UI", 9, "bold")).pack(pady=4)

    # ── Page routing ──
    def _switch_page(self, name):
        if name == self.current_page:
            return
        for n, b in self.nav_btns.items():
            b.set_active(n == name)
        self.current_page = name
        for w in self.content.winfo_children():
            w.destroy()
        pages = {
            "Dashboard":    self._show_dashboard,
            "Doctors":      self._show_doctors,
            "Patients":     self._show_patients,
            "Appointments": self._show_appointments,
            "Payments":     self._show_payments,
        }
        pages.get(name, self._show_dashboard)()

    def _page_header(self, title, subtitle=""):
        hdr = tk.Frame(self.content, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(24, 6))
        tk.Label(hdr, text=title, bg=BG, fg=TEXT, font=FONT_MED).pack(anchor="w")
        if subtitle:
            tk.Label(hdr, text=subtitle, bg=BG, fg=TEXT_MID, font=FONT_SMALL).pack(anchor="w")
        tk.Frame(self.content, bg=BORDER, height=1).pack(fill="x", padx=28, pady=(0, 18))

    # ─── DASHBOARD PAGE ───
    def _show_dashboard(self):
        self._page_header("Dashboard", "Welcome back — here's your overview")

        doctors_count = self._db_fetch("SELECT COUNT(*) FROM doctors")
        patients_count = self._db_fetch("SELECT COUNT(*) FROM patients")
        appts_count = self._db_fetch("SELECT COUNT(*) FROM appointments")
        revenue_total = self._db_fetch("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_status='Paid'")

        doctors_val = str(doctors_count[0][0]) if doctors_count else "0"
        patients_val = str(patients_count[0][0]) if patients_count else "0"
        appts_val = str(appts_count[0][0]) if appts_count else "0"
        revenue_val = f"₹{revenue_total[0][0]}" if revenue_total else "₹0"

        # Stat cards row
        cards_frame = tk.Frame(self.content, bg=BG)
        cards_frame.pack(fill="x", padx=28, pady=(0, 20))

        stats = [
            ("👨‍⚕️", doctors_val,  "Doctors",         ACCENT),
            ("🧑‍🤝‍🧑", patients_val, "Patients",        SUCCESS),
            ("📅", appts_val,      "Appointments",    WARNING),
            ("💳", revenue_val,    "Paid Revenue",    "#C678DD"),
        ]
        for i, (icon, val, lbl, col) in enumerate(stats):
            c = StatCard(cards_frame, icon, val, lbl, col)
            c.grid(row=0, column=i, padx=(0, 14), sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)

        # Two column lower section
        lower = tk.Frame(self.content, bg=BG)
        lower.pack(fill="both", expand=True, padx=28)
        lower.columnconfigure(0, weight=2)
        lower.columnconfigure(1, weight=1)

        # Appointments table
        appt_card = tk.Frame(lower, bg=CARD, highlightbackground=BORDER,
                             highlightthickness=1)
        appt_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        tk.Label(appt_card, text="Recent Appointments", bg=CARD, fg=TEXT,
                 font=FONT_BOLD).pack(anchor="w", padx=16, pady=(14, 8))

        cols = ("Patient", "Doctor", "Date", "Status")
        tree = ttk.Treeview(appt_card, columns=cols, show="headings", height=7)
        self._style_tree(tree)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=140, anchor="w")

        recent_appts = self._db_fetch(
            """
            SELECT p.name, d.name, a.appointment_date, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            ORDER BY a.appointment_date DESC, a.appointment_id DESC
            LIMIT 7
            """
        ) or []

        for row in recent_appts:
            tree.insert("", "end", values=row)

        tree.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # Quick actions card
        qa_card = tk.Frame(lower, bg=CARD, highlightbackground=BORDER,
                           highlightthickness=1)
        qa_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(qa_card, text="Quick Actions", bg=CARD, fg=TEXT,
                 font=FONT_BOLD).pack(anchor="w", padx=16, pady=(14, 12))

        actions = [
            ("+ Add Patient",     ACCENT,   "🧑"),
            ("+ Book Appointment",SUCCESS,   "📅"),
            ("+ Add Doctor",      "#C678DD", "👨‍⚕️"),
            ("⬇  Generate Report", WARNING,  "📊"),
        ]
        for txt, col, ico in actions:
            action_cmd = {
                "+ Add Patient": self._open_add_patient_dialog,
                "+ Book Appointment": self._open_book_appointment_dialog,
                "+ Add Doctor": self._open_add_doctor_dialog,
                "⬇  Generate Report": lambda: self._notify("Report", "Report generation is not implemented yet."),
            }.get(txt)
            RoundedButton(qa_card, txt, width=168, height=38,
                          command=action_cmd,
                          bg=PANEL, fg=col, hover_bg=BORDER,
                          font=("Segoe UI", 9, "bold"), radius=8
                          ).pack(pady=5)

    # ─── DOCTORS PAGE ───
    def _show_doctors(self):
        self._page_header("Doctors", "Manage hospital staff and specialists")

        toolbar = tk.Frame(self.content, bg=BG)
        toolbar.pack(fill="x", padx=28, pady=(0, 12))
        RoundedButton(toolbar, "+ Add Doctor", width=130, height=36, bg=ACCENT,
                      command=self._open_add_doctor_dialog,
                      font=("Segoe UI", 9, "bold")).pack(side="left")

        search_f = tk.Frame(toolbar, bg=PANEL, highlightbackground=BORDER,
                            highlightthickness=1)
        search_f.pack(side="right")
        tk.Label(search_f, text="🔍", bg=PANEL, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side="left", padx=8)
        tk.Entry(search_f, bg=PANEL, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", font=FONT_SMALL, width=22,
                 highlightthickness=0).pack(side="left", pady=6, padx=(0, 8))

        cols = ("Doctor ID", "Name", "Specialization", "Phone")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=14)
        self._style_tree(tree)
        widths = [90, 220, 220, 140]
        for c, w in zip(cols, widths):
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor="w")

        doctors = self._db_fetch(
            "SELECT doctor_id, name, specialization, phone FROM doctors ORDER BY doctor_id"
        ) or []
        for row in doctors:
            tree.insert("", "end", values=row)

        sb = ttk.Scrollbar(self.content, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(fill="both", expand=True, padx=28)
        sb.pack(side="right", fill="y", padx=(0, 28))

    # ─── PATIENTS PAGE ───
    def _show_patients(self):
        self._page_header("Patients", "Patient records and management")

        toolbar = tk.Frame(self.content, bg=BG)
        toolbar.pack(fill="x", padx=28, pady=(0, 12))
        RoundedButton(toolbar, "+ Register Patient", width=150, height=36,
                      command=self._open_add_patient_dialog,
                      bg=SUCCESS, font=("Segoe UI", 9, "bold")).pack(side="left")

        cols = ("Patient ID", "Name", "Age", "Gender", "Phone")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=14)
        self._style_tree(tree)
        widths = [90, 220, 90, 120, 170]
        for c, w in zip(cols, widths):
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor="w")

        patients = self._db_fetch(
            "SELECT patient_id, name, age, gender, phone FROM patients ORDER BY patient_id"
        ) or []
        for row in patients:
            tree.insert("", "end", values=row)
        tree.pack(fill="both", expand=True, padx=28)

    # ─── APPOINTMENTS PAGE ───
    def _show_appointments(self):
        self._page_header("Appointments", "Schedule and manage appointments")

        toolbar = tk.Frame(self.content, bg=BG)
        toolbar.pack(fill="x", padx=28, pady=(0, 12))
        RoundedButton(toolbar, "+ Book Appointment", width=160, height=36,
                      command=self._open_book_appointment_dialog,
                      bg=WARNING, fg=BG, font=("Segoe UI", 9, "bold")).pack(side="left")

        cols = ("Appointment ID", "Patient", "Doctor", "Date", "Status")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=14)
        self._style_tree(tree)
        widths = [120, 200, 200, 140, 120]
        for c, w in zip(cols, widths):
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor="w")

        appts = self._db_fetch(
            """
            SELECT a.appointment_id, p.name, d.name, a.appointment_date, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            ORDER BY a.appointment_id
            """
        ) or []
        for row in appts:
            tree.insert("", "end", values=row)
        tree.pack(fill="both", expand=True, padx=28)

    # ─── PAYMENTS PAGE ───
    def _show_payments(self):
        self._page_header("Payments", "Billing and financial records")

        paid_total = self._db_fetch("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_status='Paid'")
        pending_total = self._db_fetch("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_status='Pending'")
        payment_count = self._db_fetch("SELECT COUNT(*) FROM payments")

        paid_val = str(paid_total[0][0]) if paid_total else "0"
        pending_val = str(pending_total[0][0]) if pending_total else "0"
        count_val = str(payment_count[0][0]) if payment_count else "0"

        # Summary row
        summary = tk.Frame(self.content, bg=BG)
        summary.pack(fill="x", padx=28, pady=(0, 16))
        for val, lbl, col in [(f"₹{paid_val}", "Paid Amount", ACCENT),
                               (f"₹{pending_val}", "Pending Amount", DANGER),
                               (count_val, "Total Payments", WARNING)]:
            f = tk.Frame(summary, bg=CARD, highlightbackground=BORDER,
                         highlightthickness=1, padx=20, pady=12)
            f.pack(side="left", padx=(0, 12))
            tk.Label(f, text=val, bg=CARD, fg=col, font=FONT_MED).pack()
            tk.Label(f, text=lbl, bg=CARD, fg=TEXT_MID, font=FONT_SMALL).pack()

        cols = ("Payment ID", "Appointment ID", "Patient", "Date", "Amount", "Status")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=10)
        self._style_tree(tree)
        widths = [110, 130, 180, 140, 120, 120]
        for c, w in zip(cols, widths):
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor="w")

        payments = self._db_fetch(
            """
            SELECT py.payment_id, py.appointment_id, p.name, a.appointment_date, py.amount, py.payment_status
            FROM payments py
            JOIN appointments a ON py.appointment_id = a.appointment_id
            JOIN patients p ON a.patient_id = p.patient_id
            ORDER BY py.payment_id
            """
        ) or []
        for row in payments:
            tree.insert("", "end", values=row)
        tree.pack(fill="both", expand=True, padx=28)

    # ─── TREEVIEW STYLING ───
    def _style_tree(self, tree):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                         background=CARD, fieldbackground=CARD,
                         foreground=TEXT, rowheight=32,
                         font=FONT_SMALL,
                         borderwidth=0, relief="flat")
        style.configure("Treeview.Heading",
                         background=PANEL, foreground=TEXT_MID,
                         font=("Segoe UI", 9, "bold"),
                         relief="flat", borderwidth=0)
        style.map("Treeview",
                  background=[("selected", ACCENT2)],
                  foreground=[("selected", WHITE)])
        style.map("Treeview.Heading",
                  background=[("active", BORDER)])

    def _logout(self):
        self.root.destroy()
        LoginWindow().run()

    def run(self):
        self.root.mainloop()


# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────
if __name__ == "__main__":
    try:
        LoginWindow().run()
    except KeyboardInterrupt:
        pass