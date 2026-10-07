import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


def get_db_connection():
    conn = sqlite3.connect("clean_storage.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def format_date_to_human(date_str):
    """Преобразование ГГГГ-ММ-ДД в ДД.ММ.ГГГГ"""
    if not date_str:
        return ""
    parts = date_str.split("-")
    if len(parts) == 3:
        return f"{parts[2]}.{parts[1]}.{parts[0]}"
    return date_str


class PlaceholderEntry(tk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "#888888"
        self.default_fg = self["fg"]

        self.put_placeholder()
        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

    def put_placeholder(self):
        if not self.get():
            self.insert(0, self.placeholder)
            self["fg"] = self.placeholder_color

    def focus_in(self, *args):
        if self["fg"] == self.placeholder_color:
            self.delete(0, tk.END)
            self["fg"] = self.default_fg

    def focus_out(self, *args):
        if not self.get():
            self.put_placeholder()


def get_partners_data(cursor):
    """Запрос данных партнеров через обязательный параметр cursor"""
    query = "SELECT id, partner_name, inn, email FROM partners ORDER BY id ASC;"
    cursor.execute(query)
    return cursor.fetchall()


class PartnerEditWindow(tk.Toplevel):
    def __init__(self, parent, conn, mode="add", partner_id=None):
        super().__init__(parent)
        self.parent = parent
        self.conn = conn
        self.mode = mode
        self.partner_id = partner_id

        self.title("CRM: Карточка партнера [Добавление]" if mode == "add" else "CRM: Карточка партнера [Редактирование]")
        self.geometry("500x480")
        self.configure(bg="#F4F4F4")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        if self.mode == "edit" and self.partner_id:
            self.load_data()

    def create_widgets(self):
        header = tk.Frame(self, bg="#FFFFFF", pady=12, padx=20, bd=1, relief="solid")
        header.pack(fill="x")
        title_lbl = "Новый партнер" if self.mode == "add" else "Редактирование партнера"
        tk.Label(header, text=title_lbl, font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#222222").pack(side="left")

        form = tk.Frame(self, bg="#F4F4F4", padx=25, pady=15)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Наименование партнера *", font=("Segoe UI", 9, "bold"), bg="#F4F4F4").pack(anchor="w")
        self.name_entry = PlaceholderEntry(form, "ООО 'Вектор'", font=("Segoe UI", 10), bd=1, relief="solid")
        self.name_entry.pack(fill="x", ipady=4, pady=(2, 8))

        tk.Label(form, text="ИНН *", font=("Segoe UI", 9, "bold"), bg="#F4F4F4").pack(anchor="w")
        self.inn_entry = PlaceholderEntry(form, "7701234567", font=("Segoe UI", 10), bd=1, relief="solid")
        self.inn_entry.pack(fill="x", ipady=4, pady=(2, 8))

        tk.Label(form, text="Email *", font=("Segoe UI", 9, "bold"), bg="#F4F4F4").pack(anchor="w")
        self.email_entry = PlaceholderEntry(form, "vector@mail.ru", font=("Segoe UI", 10), bd=1, relief="solid")
        self.email_entry.pack(fill="x", ipady=4, pady=(2, 8))

        btn_box = tk.Frame(self, bg="#F4F4F4", padx=25, pady=15)
        btn_box.pack(fill="x", side="bottom")

        tk.Button(btn_box, text="Сохранить", font=("Segoe UI", 10, "bold"), bg="#67BA80", fg="#FFFFFF", padx=15, pady=6, relief="flat", command=self.save_data).pack(side="left")
        tk.Button(btn_box, text="Отмена", font=("Segoe UI", 10), bg="#FFFFFF", fg="#333333", padx=15, pady=6, command=self.destroy).pack(side="right")

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT partner_name, inn, email FROM partners WHERE id = ?;", (self.partner_id,))
        row = cursor.fetchone()
        if row:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, row[0])
            self.name_entry["fg"] = "#000000"

            self.inn_entry.delete(0, tk.END)
            self.inn_entry.insert(0, row[1])
            self.inn_entry["fg"] = "#000000"

            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, row[2])
            self.email_entry["fg"] = "#000000"

    def save_data(self):
        name = self.name_entry.get().strip()
        inn = self.inn_entry.get().strip()
        email = self.email_entry.get().strip()

        if name == self.name_entry.placeholder or not name:
            messagebox.showwarning("Предупреждение", "Укажите наименование партнера!")
            return
        if inn == self.inn_entry.placeholder or not inn:
            messagebox.showwarning("Предупреждение", "Укажите ИНН партнера!")
            return
        if email == self.email_entry.placeholder or not email or "@" not in email:
            messagebox.showerror("Ошибка", "Укажите корректный Email!")
            return

        cursor = self.conn.cursor()
        try:
            if self.mode == "add":
                cursor.execute("INSERT INTO partners (partner_name, inn, email) VALUES (?, ?, ?);", (name, inn, email))
            else:
                cursor.execute("UPDATE partners SET partner_name=?, inn=?, email=? WHERE id=?;", (name, inn, email, self.partner_id))
            self.conn.commit()
            self.parent.refresh_list()
            self.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка БД", "Партнер с таким ИНН или Email уже существует!")


class PartnerHistoryWindow(tk.Toplevel):
    def __init__(self, parent, conn, partner_id, partner_name):
        super().__init__(parent)
        self.parent = parent
        self.conn = conn
        self.partner_id = partner_id

        self.title(f"CRM: История продаж — {partner_name}")
        self.geometry("650x400")
        self.configure(bg="#F4F4F4")

        self.transient(parent)
        self.grab_set()

        header = tk.Frame(self, bg="#FFFFFF", pady=10, padx=15, bd=1, relief="solid")
        header.pack(fill="x")
        tk.Label(header, text=f"История реализации: {partner_name}", font=("Segoe UI", 11, "bold"), bg="#FFFFFF").pack(side="left")

        container = tk.Frame(self, bg="#F4F4F4", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        cols = ("product_name", "quantity", "amount", "sale_date")
        self.tree = ttk.Treeview(container, columns=cols, show="headings", height=9)
        self.tree.heading("product_name", text="Товар")
        self.tree.heading("quantity", text="Кол-во (шт.)")
        self.tree.heading("amount", text="Сумма (руб.)")
        self.tree.heading("sale_date", text="Дата продажи")

        self.tree.column("product_name", width=220, anchor="w")
        self.tree.column("quantity", width=100, anchor="center")
        self.tree.column("amount", width=120, anchor="e")
        self.tree.column("sale_date", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_history()

    def load_history(self):
        cursor = self.conn.cursor()
        
        query = """
            SELECT pr.product_name, sh.quantity, sh.amount, sh.sale_date
            FROM sales_history sh
            JOIN products pr ON sh.product_id = pr.id
            WHERE sh.partner_id = ?
            ORDER BY sh.sale_date DESC;
        """
        cursor.execute(query, (self.partner_id,))
        for row in cursor.fetchall():
            formatted_date = format_date_to_human(row[3])
            self.tree.insert("", "end", values=(row[0], f"{row[1]} шт.", f"{row[2]:,.2f} руб.", formatted_date))


class MainWindow(tk.Tk):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.title("CRM: Реестр партнеров")
        self.geometry("800x550")
        self.configure(bg="#F4F4F4")

        self.edit_window = None
        self.history_window = None

        header = tk.Frame(self, bg="#FFFFFF", padx=20, pady=12, bd=1, relief="solid")
        header.pack(fill="x")

        logo_canvas = tk.Canvas(header, width=36, height=36, bg="#67BA80", highlightthickness=0)
        logo_canvas.pack(side="left", padx=(0, 12))
        logo_canvas.create_oval(4, 4, 32, 32, fill="#FFFFFF", outline="")
        logo_canvas.create_text(18, 18, text="МП", font=("Segoe UI", 9, "bold"), fill="#67BA80")

        tk.Label(header, text="Реестр партнеров и продаж", font=("Segoe UI", 13, "bold"), bg="#FFFFFF").pack(side="left")

        controls = tk.Frame(self, bg="#F4F4F4", padx=20, pady=10)
        controls.pack(fill="x")

        tk.Button(controls, text="+ Добавить партнера", font=("Segoe UI", 10, "bold"), bg="#67BA80", fg="#FFFFFF", padx=12, pady=5, relief="flat", command=self.open_add_partner).pack(side="left")

        self.list_frame = tk.Frame(self, bg="#F4F4F4", padx=20, pady=5)
        self.list_frame.pack(fill="both", expand=True)

        self.refresh_list()

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        cursor = self.conn.cursor()
        partners = get_partners_data(cursor)

        for p in partners:
            pid, name, inn, email = p
            card = tk.Frame(self.list_frame, bg="#FFFFFF", bd=1, relief="solid", padx=15, pady=10)
            card.pack(fill="x", pady=4)

            top = tk.Frame(card, bg="#FFFFFF")
            top.pack(fill="x")

            tk.Label(top, text=f"ID {pid}: {name}", font=("Segoe UI", 11, "bold"), bg="#FFFFFF").pack(side="left")
            tk.Button(top, text="История реализации", font=("Segoe UI", 9), bg="#FFFFFF", command=lambda partner_id=pid, partner_name=name: self.open_history(partner_id, partner_name)).pack(side="right")

            tk.Label(card, text=f"ИНН: {inn} | Email: {email}", font=("Segoe UI", 9), bg="#FFFFFF", fg="#555555").pack(anchor="w", pady=(2, 0))

    def open_add_partner(self):
        if self.edit_window is None or not self.edit_window.winfo_exists():
            self.edit_window = PartnerEditWindow(self, self.conn, mode="add")
        else:
            self.edit_window.lift()

    def open_history(self, partner_id, partner_name):
        if self.history_window is None or not self.history_window.winfo_exists():
            self.history_window = PartnerHistoryWindow(self, self.conn, partner_id, partner_name)
        else:
            self.history_window.lift()


if __name__ == "__main__":
    conn = get_db_connection()
    app = MainWindow(conn)
    app.mainloop()
