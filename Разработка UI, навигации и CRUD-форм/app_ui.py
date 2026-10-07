import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


def get_db_connection():
    conn = sqlite3.connect("master_floor.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def format_date_to_human(date_str):
    """Форматирование даты из ГГГГ-ММ-ДД в ДД.ММ.ГГГГ"""
    if not date_str:
        return ""
    if "-" in date_str:
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
    """Корректная функция получения данных через аргумент cursor"""
    query = """
        SELECT p.id, pt.type_name, p.name, p.director_name, p.email, p.phone, p.rating
        FROM partners p
        JOIN partner_types pt ON p.type_id = pt.id
        ORDER BY p.id DESC;
    """
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
        self.geometry("520x620")
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

        title_lbl = "Создание карточки партнера" if self.mode == "add" else "Редактирование карточки"
        tk.Label(header, text=title_lbl, font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#222222").pack(side="left")

        form = tk.Frame(self, bg="#F4F4F4", padx=25, pady=15)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Наименование партнера *", font=("Segoe UI", 9, "bold"), bg="#F4F4F4").pack(anchor="w")
        self.name_entry = PlaceholderEntry(form, "Например: ООО 'Паркет 29'", font=("Segoe UI", 10), bd=1, relief="solid")
        self.name_entry.pack(fill="x", ipady=4, pady=(2, 8))

        tk.Label(form, text="Тип партнера *", font=("Segoe UI", 9, "bold"), bg="#F4F4F4").pack(anchor="w")
        self.type_combo = ttk.Combobox(form, font=("Segoe UI", 10), state="readonly")
        self.type_combo.pack(fill="x", ipady=3, pady=(2, 8))
        self.load_types()

        tk.Label(form, text="Рейтинг *", font=("Segoe UI", 9, "bold"), bg="#F4F4F4").pack(anchor="w")
        self.rating_entry = tk.Entry(form, font=("Segoe UI", 10), bd=1, relief="solid")
        self.rating_entry.insert(0, "0")
        self.rating_entry.pack(fill="x", ipady=4, pady=(2, 8))

        tk.Label(form, text="ФИО директора", font=("Segoe UI", 9, "bold"), bg="#F4F4F4").pack(anchor="w")
        self.director_entry = PlaceholderEntry(form, "Петров Петр Петрович", font=("Segoe UI", 10), bd=1, relief="solid")
        self.director_entry.pack(fill="x", ipady=4, pady=(2, 8))

        tk.Label(form, text="Телефон *", font=("Segoe UI", 9, "bold"), bg="#F4F4F4").pack(anchor="w")
        self.phone_entry = PlaceholderEntry(form, "+7 (921) 555-44-33", font=("Segoe UI", 10), bd=1, relief="solid")
        self.phone_entry.pack(fill="x", ipady=4, pady=(2, 8))

        tk.Label(form, text="Email *", font=("Segoe UI", 9, "bold"), bg="#F4F4F4").pack(anchor="w")
        self.email_entry = PlaceholderEntry(form, "parket29@mail.ru", font=("Segoe UI", 10), bd=1, relief="solid")
        self.email_entry.pack(fill="x", ipady=4, pady=(2, 8))

        btn_box = tk.Frame(self, bg="#F4F4F4", padx=25, pady=15)
        btn_box.pack(fill="x", side="bottom")

        tk.Button(btn_box, text="Сохранить", font=("Segoe UI", 10, "bold"), bg="#67BA80", fg="#FFFFFF", padx=15, pady=6, relief="flat", command=self.save_data).pack(side="left")
        tk.Button(btn_box, text="Отмена", font=("Segoe UI", 10), bg="#FFFFFF", fg="#333333", padx=15, pady=6, command=self.destroy).pack(side="right")

    def load_types(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, type_name FROM partner_types;")
        self.types_map = {row[1]: row[0] for row in cursor.fetchall()}
        self.type_combo["values"] = list(self.types_map.keys())
        if self.type_combo["values"]:
            self.type_combo.current(0)

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT pt.type_name, p.name, p.director_name, p.email, p.phone, p.rating
            FROM partners p JOIN partner_types pt ON p.type_id = pt.id WHERE p.id = ?;
        """, (self.partner_id,))
        row = cursor.fetchone()
        if row:
            self.type_combo.set(row[0])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, row[1])
            self.name_entry["fg"] = "#000000"
            if row[2]:
                self.director_entry.delete(0, tk.END)
                self.director_entry.insert(0, row[2])
                self.director_entry["fg"] = "#000000"
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, row[3])
            self.email_entry["fg"] = "#000000"
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, row[4])
            self.phone_entry["fg"] = "#000000"
            self.rating_entry.delete(0, tk.END)
            self.rating_entry.insert(0, str(row[5]))

    def save_data(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        if name == self.name_entry.placeholder or not name:
            messagebox.showerror("Ошибка", "Заполните наименование партнера!")
            return
        if email == self.email_entry.placeholder or not email:
            messagebox.showerror("Ошибка", "Заполните Email!")
            return

        type_id = self.types_map.get(self.type_combo.get(), 1)
        director = self.director_entry.get().strip()
        if director == self.director_entry.placeholder:
            director = ""
        phone = self.phone_entry.get().strip()
        if phone == self.phone_entry.placeholder:
            phone = ""

        try:
            rating = int(self.rating_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть целым числом!")
            return

        cursor = self.conn.cursor()
        if self.mode == "add":
            cursor.execute("""
                INSERT INTO partners (type_id, name, director_name, email, phone, inn, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (type_id, name, director, email, phone, f"78{hash(name)%100000000:08d}", rating))
        else:
            cursor.execute("""
                UPDATE partners SET type_id=?, name=?, director_name=?, email=?, phone=?, rating=?
                WHERE id=?;
            """, (type_id, name, director, email, phone, rating, self.partner_id))

        self.conn.commit()
        self.parent.refresh_list()
        self.destroy()


class PartnerHistoryWindow(tk.Toplevel):
    def __init__(self, parent, conn, partner_id, partner_name):
        super().__init__(parent)
        self.parent = parent
        self.conn = conn
        self.partner_id = partner_id

        self.title(f"CRM: История реализации — {partner_name}")
        self.geometry("650x420")
        self.configure(bg="#F4F4F4")

        self.transient(parent)
        self.grab_set()

        header = tk.Frame(self, bg="#FFFFFF", pady=10, padx=15, bd=1, relief="solid")
        header.pack(fill="x")
        tk.Label(header, text=f"История реализации продукции: {partner_name}", font=("Segoe UI", 11, "bold"), bg="#FFFFFF").pack(side="left")

        container = tk.Frame(self, bg="#F4F4F4", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        cols = ("product_name", "quantity", "sale_date")
        self.tree = ttk.Treeview(container, columns=cols, show="headings", height=10)
        self.tree.heading("product_name", text="Продукция")
        self.tree.heading("quantity", text="Количество (шт.)")
        self.tree.heading("sale_date", text="Дата продажи")

        self.tree.column("product_name", width=300, anchor="w")
        self.tree.column("quantity", width=120, anchor="center")
        self.tree.column("sale_date", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_history()

    def load_history(self):
        cursor = self.conn.cursor()
        
        query = """
            SELECT pr.product_name, sh.quantity, sh.sale_date
            FROM sales_history sh
            JOIN products pr ON sh.product_id = pr.id
            WHERE sh.partner_id = ?
            ORDER BY sh.sale_date DESC;
        """
        cursor.execute(query, (self.partner_id,))
        for row in cursor.fetchall():
            
            formatted_date = format_date_to_human(row[2])
            self.tree.insert("", "end", values=(row[0], f"{row[1]} шт.", formatted_date))


class MainWindow(tk.Tk):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.title("CRM: Мастер Пол — Реестр партнеров")
        self.geometry("820x620")
        self.configure(bg="#F4F4F4")

        self.set_icon()
        self.edit_window = None
        self.history_window = None

        header = tk.Frame(self, bg="#FFFFFF", padx=20, pady=12, bd=1, relief="solid")
        header.pack(fill="x")

        logo_canvas = tk.Canvas(header, width=40, height=40, bg="#67BA80", highlightthickness=0)
        logo_canvas.pack(side="left", padx=(0, 15))
        logo_canvas.create_oval(5, 5, 35, 35, fill="#FFFFFF", outline="")
        logo_canvas.create_text(20, 20, text="МП", font=("Segoe UI", 10, "bold"), fill="#67BA80")

        title_box = tk.Frame(header, bg="#FFFFFF")
        title_box.pack(side="left")
        tk.Label(title_box, text="Мастер Пол", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#222222").pack(anchor="w")
        tk.Label(title_box, text="Система взаимодействия с партнерами", font=("Segoe UI", 9), bg="#FFFFFF", fg="#777777").pack(anchor="w")

        controls = tk.Frame(self, bg="#F4F4F4", padx=20, pady=10)
        controls.pack(fill="x")

        tk.Button(controls, text="+ Добавить партнера", font=("Segoe UI", 10, "bold"), bg="#67BA80", fg="#FFFFFF", padx=12, pady=5, relief="flat", command=self.open_add_partner).pack(side="left")

        self.list_frame = tk.Frame(self, bg="#F4F4F4", padx=20, pady=5)
        self.list_frame.pack(fill="both", expand=True)

        self.refresh_list()

    def set_icon(self):
        try:
            icon_img = tk.PhotoImage(width=16, height=16)
            icon_img.put("#67BA80", to=(0, 0, 15, 15))
            self.iconphoto(True, icon_img)
        except Exception:
            pass

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        cursor = self.conn.cursor()
        partners = get_partners_data(cursor)

        for p in partners:
            pid, ptype, name, director, email, phone, rating = p
            card = tk.Frame(self.list_frame, bg="#FFFFFF", bd=1, relief="solid", padx=15, pady=10)
            card.pack(fill="x", pady=5)

            top = tk.Frame(card, bg="#FFFFFF")
            top.pack(fill="x")

            tk.Label(top, text=f"{ptype} | {name}", font=("Segoe UI", 11, "bold"), bg="#FFFFFF").pack(side="left")
            tk.Button(top, text="История реализации", font=("Segoe UI", 9), bg="#FFFFFF", command=lambda partner_id=pid, partner_name=name: self.open_history(partner_id, partner_name)).pack(side="right")

            tk.Label(card, text=f"Директор: {director or 'Не указан'} | Тел: {phone} | Рейтинг: {rating}", font=("Segoe UI", 9), bg="#FFFFFF", fg="#555555").pack(anchor="w", pady=(4, 0))

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
