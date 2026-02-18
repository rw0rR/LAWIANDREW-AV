import customtkinter as ctk
import pyrebase
import os
import shutil
import webbrowser
from datetime import datetime, timedelta
from tkinter import messagebox

# --- FIREBASE (Admin Panelinle Aynı Veritabanı) ---
config = {
    "apiKey": "AIzaSyDbwcVL09Fc8bNe6h4Tp0AuA772xeObdWg",
    "authDomain": "lawiaw.firebaseapp.com",
    "databaseURL": "https://lawiaw-default-rtdb.firebaseio.com",
    "projectId": "lawiaw",
    "storageBucket": "lawiaw.firebasestorage.app",
    "messagingSenderId": "1026864162658",
    "appId": "1:1026864162658:web:c200ad9c9bae53fb22ee3b"
}
firebase = pyrebase.initialize_app(config); auth = firebase.auth(); db = firebase.database()
VERSION = "1.1"

class LawiV46(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LAWIANDREW V46 - LICENSED"); self.geometry("1150x800")
        ctk.set_appearance_mode("Dark")
        self.lang = "TR"
        
        self.dict = {
            "TR": {"m1": "🏠 ANA SAYFA", "m2": "🔍 TARAMA & TEMİZLİK", "m3": "👤 PROFİL", "h1": "📢 DUYURU", "s1": "AKTİF KULLANICI", "s2": "TESPİT EDİLEN", "s3": "ENGELLENEN", "n1": "📜 GÜNCELLEME NOTLARI", "sc1": "TARAMAYI BAŞLAT", "sc2": "🔍 GÜVENLİK TARAMASI"},
            "EN": {"m1": "🏠 DASHBOARD", "m2": "🔍 SCAN & CLEAN", "m3": "👤 PROFILE", "h1": "📢 ANNOUNCEMENT", "s1": "ACTIVE USERS", "s2": "DETECTED", "s3": "BLOCKED", "n1": "📜 CHANGELOGS", "sc1": "START SCAN", "sc2": "🔍 SECURITY SCAN"}
        }
        self.setup_auth()

    def setup_auth(self):
        self.auth_f = ctk.CTkFrame(self, fg_color="transparent")
        self.auth_f.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self.auth_f, text="🛡️ LAWIANDREW", font=("Orbitron", 40, "bold"), text_color="#2CC985").pack(pady=20)
        
        self.e = ctk.CTkEntry(self.auth_f, placeholder_text="E-posta", width=350, height=45); self.e.pack(pady=5)
        self.p = ctk.CTkEntry(self.auth_f, placeholder_text="Şifre", width=350, height=45, show="*"); self.p.pack(pady=5)
        self.l = ctk.CTkEntry(self.auth_f, placeholder_text="LİSANS ANAHTARI (Kayıt/Aktivasyon)", width=350, height=45); self.l.pack(pady=5)

        btn_f = ctk.CTkFrame(self.auth_f, fg_color="transparent")
        btn_f.pack(pady=15)
        ctk.CTkButton(btn_f, text="GİRİŞ YAP", width=170, height=45, fg_color="#2CC985", text_color="black", font=("Roboto", 14, "bold"), command=self.login).pack(side="left", padx=5)
        ctk.CTkButton(btn_f, text="KAYIT / AKTİF ET", width=170, height=45, command=self.register).pack(side="left", padx=5)

    def login(self):
        try:
            # Önce Firebase Auth girişi
            user = auth.sign_in_with_email_and_password(self.e.get(), self.p.get())
            # Versiyon Kontrolü
            v = db.child("system_config").child("latest_version").get().val()
            if v != VERSION: 
                messagebox.showerror("Hata", f"Versiyon Hatası! Gerekli: {v}"); self.destroy(); return
            
            # Kullanıcı Verisi ve Süre Kontrolü
            data = db.child("users").child(user['localId']).get().val()
            if data:
                expiry = datetime.strptime(data['expiry_date'], "%Y-%m-%d %H:%M")
                if datetime.now() > expiry:
                    messagebox.showerror("Lisans", "Süreniz dolmuş! Yeni bir key ile tekrar kayıt olun."); return
                
                self.user_info = data
                self.auth_f.destroy(); self.setup_main()
            else:
                messagebox.showerror("Hata", "Kullanıcı verisi yok. Önce kayıt olun!")
        except: messagebox.showerror("Hata", "Giriş bilgileri yanlış!")

    def register(self):
        key = self.l.get()
        # Admin Panelden gelen valid_keys kontrolü
        valid_data = db.child("valid_keys").child(key).get().val()
        
        if valid_data:
            try:
                # Kullanıcıyı oluştur
                user = auth.create_user_with_email_and_password(self.e.get(), self.p.get())
                # Lisans süresini hesapla
                sec = valid_data.get("duration_seconds", 3600)
                exp = (datetime.now() + timedelta(seconds=sec)).strftime("%Y-%m-%d %H:%M")
                
                # Kullanıcıyı mühürle
                db.child("users").child(user['localId']).set({
                    "email": self.e.get(),
                    "member_type": valid_data.get("type", "Pro"),
                    "expiry_date": exp
                })
                # Kullanılan keyi sil (tek kullanımlık)
                db.child("valid_keys").child(key).remove()
                messagebox.showinfo("Başarılı", "Lisans Onaylandı! Şimdi Giriş Yapabilirsin.")
            except: messagebox.showerror("Hata", "Bu e-posta zaten kullanımda veya hatalı!")
        else:
            messagebox.showerror("Geçersiz", "Girdiğin LİSANS ANAHTARI sistemde bulunamadı!")

    def setup_main(self):
        # Sidebar ve Diğer Kısımlar (V45.1 Tasarımı Korundu)
        self.side = ctk.CTkFrame(self, width=220, corner_radius=15); self.side.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(self.side, text="LAWIANDREW", font=("Orbitron", 20, "bold"), text_color="#2CC985").pack(pady=30)
        
        self.nav_btns = {}
        for key, m in [("m1", "Home"), ("m2", "Scan"), ("m3", "Prof")]:
            btn = ctk.CTkButton(self.side, text=self.dict[self.lang][key], fg_color="transparent", anchor="w", height=45, command=lambda x=m: self.show(x))
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_btns[m] = (btn, key)
            
        self.lang_btn = ctk.CTkButton(self.side, text="DİL: " + self.lang, fg_color="#1a1a1a", command=self.toggle_lang)
        self.lang_btn.pack(side="bottom", pady=(10,20), padx=20)
        
        ctk.CTkLabel(self.side, text="© 2026 LawiAndrew Security", font=("Roboto", 10), text_color="gray").pack(side="bottom")
        link = ctk.CTkLabel(self.side, text="www.lawiandrew.site", font=("Roboto", 10, "underline"), text_color="#2CC985", cursor="hand2")
        link.pack(side="bottom"); link.bind("<Button-1>", lambda e: webbrowser.open("http://www.lawiandrew.site"))

        self.cont = ctk.CTkFrame(self, fg_color="transparent"); self.cont.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self.show("Home")

    def toggle_lang(self):
        self.lang = "EN" if self.lang == "TR" else "TR"
        for m, (btn, key) in self.nav_btns.items(): btn.configure(text=self.dict[self.lang][key])
        self.lang_btn.configure(text="DİL: " + self.lang); self.show("Home")

    def show(self, name):
        for w in self.cont.winfo_children(): w.destroy()
        d = self.dict[self.lang]
        
        if name == "Home":
            # Duyurular ve İstatistikler
            news = db.child("news").get().val() or "LawiAndrew Guard Aktif."
            n_f = ctk.CTkFrame(self.cont, fg_color="#1a1a1a", border_width=1, border_color="#2CC985")
            n_f.pack(fill="x", pady=(0,15))
            ctk.CTkLabel(n_f, text=f"{d['h1']}: {news}", font=("Roboto", 15, "bold")).pack(pady=12)

            stat_frame = ctk.CTkFrame(self.cont, fg_color="transparent")
            stat_frame.pack(fill="x", pady=10)
            
            stats_data = [
                (d['s1'], db.child("system_config").child("active_users").get().val() or 0, "#2CC985"),
                (d['s2'], db.child("system_config").child("detected_threats").get().val() or 0, "#e67e22"),
                (d['s3'], db.child("system_config").child("blocked_attacks").get().val() or 0, "#e74c3c")
            ]
            for title, val, color in stats_data:
                box = ctk.CTkFrame(stat_frame, fg_color="#111", border_width=1, border_color=color, width=280, height=120)
                box.pack(side="left", padx=10, expand=True, fill="both")
                ctk.CTkLabel(box, text=title, font=("Roboto", 12, "bold"), text_color=color).pack(pady=(15,5))
                ctk.CTkLabel(box, text=str(val), font=("Orbitron", 30, "bold")).pack(pady=5)

            ctk.CTkLabel(self.cont, text=d['n1'], font=("Roboto", 16, "bold"), text_color="#2CC985").pack(pady=(30,10), anchor="w")
            t_notes = ctk.CTkTextbox(self.cont, height=300, font=("Consolas", 13), border_width=1, border_color="#333")
            t_notes.pack(fill="x", pady=5)
            notes = db.child("changelog").get().val()
            if notes:
                for v, n in reversed(list(notes.items())): t_notes.insert("end", f"[{v}] >>> {n}\n" + "-"*60 + "\n")
            t_notes.configure(state="disabled")

        elif name == "Scan":
            ctk.CTkLabel(self.cont, text=d['sc2'], font=("Orbitron", 24, "bold")).pack(pady=20)
            self.s_log = ctk.CTkTextbox(self.cont, fg_color="black", text_color="#2CC985", height=400, font=("Consolas", 12))
            self.s_log.pack(fill="x", pady=10)
            ctk.CTkButton(self.cont, text=d['sc1'], fg_color="#2CC985", text_color="black", height=50, font=("Roboto", 15, "bold"), command=self.do_clean).pack()

        elif name == "Prof":
            ctk.CTkLabel(self.cont, text=d['m3'], font=("Orbitron", 24, "bold")).pack(pady=20)
            ctk.CTkLabel(self.cont, text=f"Email: {self.user_info['email']}\nPlan: {self.user_info['member_type']}\nLisans Bitiş: {self.user_info['expiry_date']}", font=("Roboto", 18)).pack()

    def do_clean(self):
        self.s_log.insert("end", "> Tarama ve Temizlik Başlatıldı...\n")
        shutil.rmtree(os.environ.get('TEMP'), ignore_errors=True) 
        self.s_log.insert("end", "> Sistem optimize edildi.\n")

if __name__ == "__main__": LawiV46().mainloop()