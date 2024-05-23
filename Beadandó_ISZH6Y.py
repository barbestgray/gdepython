"""
Ez a program egy egyszerű szállodai foglalási rendszert valósít meg Pythonban,
amely lehetővé teszi a felhasználók számára, hogy szobákat foglaljanak, foglalásokat
lemondjanak, valamint megtekintsék az aktuális foglalások listáját. A program tartalmaz
egy grafikus felhasználói felületet is, amely megkönnyíti a különböző műveletek
végrehajtását. A program három szobatípust (egyágyas, kétágyas) és egy szálloda osztályt
definiál, amely kezeli a szobák és foglalások nyilvántartását.
"""


import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List

# Konstansok
DATE_FORMAT = "%Y-%m-%d"
ERROR_NO_DATE = "Kérem adjon meg egy dátumot."
ERROR_NO_ROOM_NUMBER = "Kérem adjon meg egy szobaszámot."


class Room(ABC):
    """Absztrakt osztály, ami egy szállodai szoba alapvető attribútumait definiálja."""

    def __init__(self, room_number: str, price: int):
        self._room_number = room_number
        self._price = price

    @property
    def room_number(self) -> str:
        return self._room_number

    @property
    def price(self) -> int:
        return self._price

    @abstractmethod
    def get_room_type(self) -> str:
        pass


class SingleRoom(Room):
    """Osztály, ami az egyágyas szoba attribútumait tartalmazza."""

    def __init__(self, room_number: str):
        super().__init__(room_number, 50000)

    def get_room_type(self) -> str:
        return "Egyágyas"


class DoubleRoom(Room):
    """Osztály, ami a kétágyas szoba attribútumait tartalmazza."""

    def __init__(self, room_number: str):
        super().__init__(room_number, 80000)

    def get_room_type(self) -> str:
        return "Kétágyas"


class Booking:

    def __init__(self, room: Room, date: datetime):
        self.room = room
        self.date = date


class Hotel:

    def __init__(self, name: str):
        self.name = name
        self.rooms: List[Room] = []
        self.bookings: List[Booking] = []

    def add_room(self, room: Room):
        self.rooms.append(room)

    def book_room(self, room_number: str, date: str) -> int:
        """Létrehoz egy foglalást adott szobaszámra és dátumra."""
        date_obj = datetime.strptime(date, DATE_FORMAT)
        if date_obj < datetime.now():
            raise ValueError("Hibás dátum. Csak jövőbeni dátumra lehet foglalni.")
        if any(booking.room.room_number == room_number and booking.date == date_obj for booking in self.bookings):
            raise Exception("A szoba már foglalt ezen a napon.")
        for room in self.rooms:
            if room.room_number == room_number:
                new_booking = Booking(room, date_obj)
                self.bookings.append(new_booking)
                return room.price
        raise ValueError("Nincs ilyen szobaszám.")

    def cancel_booking(self, room_number: str, date: str) -> bool:
        """Töröl egy foglalást adott szobaszámra és dátumra."""
        date_obj = datetime.strptime(date, DATE_FORMAT)
        for booking in self.bookings:
            if booking.room.room_number == room_number and booking.date == date_obj:
                self.bookings.remove(booking)
                return True
        raise ValueError("Nincs ilyen foglalás ezen a napon.")

    def list_bookings(self) -> str:
        if not self.bookings:
            return "Nincsenek foglalások."
        return "\n".join(f"Szoba {booking.room.room_number}, Dátum: {booking.date.strftime(DATE_FORMAT)}"
                         for booking in self.bookings)


class HotelApp:

    def __init__(self, master: tk.Tk, hotel: Hotel):
        self.master = master
        self.hotel = hotel

        # Alap beállítások
        master.title("Hotel Foglalási Rendszer")
        master.geometry("400x300")

        # Stílus beállítások
        style = ttk.Style(master)
        style.theme_use('clam')

        # Keret létrehozása
        frame = ttk.Frame(master, padding="10 10 10 10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Gombok létrehozása
        actions = [("Szoba foglalása", self.book),
                   ("Foglalás lemondása", self.cancel),
                   ("Szobák listázása", self.list_rooms),
                   ("Foglalások listázása", self.list_bookings),
                   ("Kilépés", master.quit)]

        for text, command in actions:
            ttk.Button(frame, text=text, command=command).pack(fill=tk.X, pady=5)

    def list_rooms(self):
        room_info = '\n'.join(f"Szobaszám: {room.room_number}, Ár: {room.price} Ft" for room in self.hotel.rooms)
        messagebox.showinfo("Szobák listája", room_info)

    def book(self):
        self.show_input_dialog("Szoba foglalása", self.do_booking)

    def cancel(self):
        self.show_input_dialog("Foglalás lemondása", self.do_cancel)

    def show_input_dialog(self, title: str, command):
        top = tk.Toplevel(self.master)
        top.title(title)

        frame = ttk.Frame(top, padding="10 10 10 10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Szobaszám:").pack()
        room_number_entry = ttk.Entry(frame)
        room_number_entry.pack()

        ttk.Label(frame, text="Dátum (YYYY-MM-DD):").pack()
        date_entry = ttk.Entry(frame)
        date_entry.pack()

        ttk.Button(frame, text="OK", command=lambda: command(
            room_number_entry.get(), date_entry.get(), top)).pack(pady=10)

    def do_booking(self, room_number: str, date: str, window: tk.Toplevel):
        """Kezeli a foglalás folyamatát."""
        if not date:
            messagebox.showerror("Hiba", ERROR_NO_DATE)
            return
        if not room_number:
            messagebox.showerror("Hiba", ERROR_NO_ROOM_NUMBER)
            return
        try:
            price = self.hotel.book_room(room_number, date)
            messagebox.showinfo("Köszönjük!", f"A foglalás sikeres. Az ár: {price} Ft.")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    def do_cancel(self, room_number: str, date: str, window: tk.Toplevel):
        """Kezeli a foglalás lemondásának folyamatát."""
        if not date:
            messagebox.showerror("Hiba", ERROR_NO_DATE)
            return
        if not room_number:
            messagebox.showerror("Hiba", ERROR_NO_ROOM_NUMBER)
            return
        try:
            if self.hotel.cancel_booking(room_number, date):
                messagebox.showinfo("Köszönjük!", "A foglalás sikeresen lemondva.")
                window.destroy()
        except ValueError as e:
            messagebox.showerror("Hiba", str(e))

    def list_bookings(self):
        """Megjeleníti az összes foglalást."""
        bookings = self.hotel.list_bookings()
        messagebox.showinfo("Foglalások listája", bookings)


# Hotel létrehozása és szobák hozzáadása
hotel = Hotel("Program Hotel")
rooms_data = [
    ("egyágyas", "105"),
    ("egyágyas", "106"),
    ("kétágyas", "107"),
    # ("haromagyas", "108")  # Ismeretlen szobatípus tesztelése
]

for room_type, room_number in rooms_data:
    if room_type == "egyágyas":
        hotel.add_room(SingleRoom(room_number))
    elif room_type == "kétágyas":
        hotel.add_room(DoubleRoom(room_number))
    else:
        messagebox.showerror("Hiba", f"Ismeretlen szobatípus: {room_type}")
        exit(1)  # Program leállítása hiba esetén

# Előzetes foglalások listázása
booking_data = [
    ("105", "2024-12-01"),
    ("105", "2024-12-02"),
    ("106", "2024-07-30"),
    ("107", "2024-12-31"),
    ("107", "2025-01-01")
]

for room_number, date in booking_data:
    try:
        hotel.book_room(room_number, date)
    except Exception as e:
        print(f"Hiba a foglalás hozzáadásakor: {e}")

root = tk.Tk()
app = HotelApp(root, hotel)
root.mainloop()
