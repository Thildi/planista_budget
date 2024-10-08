import tkinter as tk
from tkinter import messagebox
import pandas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import date
from PIL import Image, ImageTk
from text_label import text_label


font = ("open sans", 15)
bold_font = ("open sans", 18, "bold")

paper_color = "#fbfbfb"
orange_color = "#fcd9a8"
dark_color = "#6addda"
blue_color = "#d0eef8"
dark_blue_color = "#3bc4cf"
green_color = "#D9EDBF"
red_color = "#FFB996"
dark_orange_color = "#FFCF81"
pink_color = "#F7B5CA"
purple_color = "#AC87C5"
yellow_color = "#F9F3CC"

color_list = [orange_color, dark_orange_color, blue_color, dark_color,
              dark_blue_color, green_color, red_color, pink_color,
              purple_color, yellow_color,
              ]

current_date = date.today().strftime("%d.%m.%Y")
current_month = date.today().month
current_year = date.today().year

cat_dict = {}

category_list = ["Lebensmittel", "Haushalt", "Kleidung", "Elektronik", "Pflanzen",
                 "Fast Food", "Ausbildung", "Fluff", "Tabakwaren",
                 "Auto", "Alkohol", "Restaurant", "Gluecksspiel",
                 "Tanken", "Sonstiges",
                 ]

shop_list = ["Penny", "Famila", "Aldi", "Growshop",
             "DM", "Rewe", "Edeka", "Amazon",
             "Kleinanzeigen", "Online Sonstiges", "Restaurant", "Tankstelle",
             "Kiosk", "Action", "Kik", "H&M", "Sonstiges",
             ]

month_list = [f"0{month}" if month < 10 else str(month) for month in range(1, 13)]

price_per_cat = []
found_cat = []

label_to_remove = []

dataframe = pandas.read_csv("planista_database.csv")
dataframe["date"] = pandas.to_datetime(dataframe["date"], format="%d.%m.%Y")

current_month_df = dataframe[dataframe["date"].dt.month == current_month]
last_month_df = dataframe[dataframe["date"].dt.month == current_month - 1]

category_sums = current_month_df.groupby("category")["price"].sum()

bad_stuff_list = []
bad_stuff_values = []

alc_sum = category_sums.get("alkohol", 0)
if alc_sum:
    bad_stuff_values.append(alc_sum)
    bad_stuff_list.append("Alkohol")

# restaurant_sum = category_sums.get("restaurant", 0)
# if restaurant_sum:
#     bad_stuff_values.append(restaurant_sum)
#     bad_stuff_list.append("Restaurant")

gambling_sum = category_sums.get("gluecksspiel", 0)
if gambling_sum:
    bad_stuff_values.append(gambling_sum)
    bad_stuff_list.append("Gluecksspiel")

tobacco_sum = category_sums.get("tabakwaren", 0)
if tobacco_sum:
    bad_stuff_values.append(tobacco_sum)
    bad_stuff_list.append("Tabakwaren")

for cat in category_list:
    cat_df = dataframe[dataframe["category"] == cat.lower()]
    cat_sum = cat_df["price"].sum()
    cat_dict[cat] = cat_sum

try:
    last_entry_df = dataframe.iloc[-1]
    last_entry_item = last_entry_df["item"]
    last_entry_price = last_entry_df["price"]
    last_entry_date = last_entry_df["date"]

except IndexError:
    last_entry_df = ""
    last_entry_item = ""
    last_entry_price = ""
    last_entry_date = ""


def update_last_entry():
    """ updates the last item bought """
    try:
        temp_df = pandas.read_csv("planista_database.csv")

        if temp_df.empty:
            last_entry_text.config(text="No entries found")
            return

        last_item = temp_df.iloc[-1]

        last_entry_text.config(text=f"Your last entry: "
                                    f"{last_item['item'].title()} - "
                                    f"{last_item['price']:.2f} EUR - "
                                    f"{last_item['date']}")

    except (KeyError, IndexError, FileNotFoundError) as e:
        last_entry_text.config(text=f"Error: {str(e)}")


def entry_klick(event):
    """ clears the entry-widget when clicking on it"""
    date_entry.delete(0, tk.END)
    date_entry.config(fg="black")


def save_data():
    """ saves the data put in """
    item = item_entry.get().lower()
    price = cost_entry.get().lower().replace(",", ".")
    category = selected_category.get().lower()
    shop = selected_shop.get().lower()
    curr_date = date_entry.get()

    if not item or not price or not category or not shop:
        messagebox.showerror("error", "All fields must be filled")
        return

    try:
        price = float(price)
    except ValueError:
        messagebox.showerror("error", "The price is not right")
        return

    new_data = pandas.DataFrame({"item": [item],
                                 "shop": [shop],
                                 "category": [category],
                                 "price": [price],
                                 "date": [curr_date],
                                 })

    new_data.to_csv("planista_database.csv", mode="a", index=False, header=False)

    item_entry.delete(0, tk.END)
    cost_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    date_entry.insert(1, current_date)
    selected_category.set("---")
    selected_shop.set("---")

    date_entry.config(fg="#d3d3d3")

    update_last_entry()
    main_window.update()


def open_stats_window():
    """ opens the statistics window and creates several widgets"""
    global cat_dict

    overall_stats_df = pandas.read_csv("planista_database.csv")
    overall_sum = round(sum(overall_stats_df["price"]), 2)

    def reset_entries():
        global label_to_remove
        selected_month.set("")
        selected_cat_stats.set("")

        for label in label_to_remove:
            label.config(text="")

        total_purchases.config(text=f"Total purchases:\n"
                                    f"Total cost:")

        new_cat_text = tk.Label(master=gui_frame_2,
                                   text=f"",
                                   font=("open sans", 16, "bold"),
                                   bg="white"
                                   )
        new_cat_text.grid(row=4, column=1, pady=10)
        label_to_remove.append(new_cat_text)

    def clear_year(event):
        """ clears the year entry widget """
        year_entry.delete(0, tk.END)
        year_entry.config(fg="black")

    def search_stats():

        global cat_dict, label_to_remove
        
        search_df = pandas.read_csv("planista_database.csv")

        try:
            chosen_month = int(selected_month.get())
        except ValueError:
            chosen_month = 0
        chosen_year = int(year_entry.get())
        chosen_cat = selected_cat_stats.get().lower()

        search_df["date"] = pandas.to_datetime(search_df["date"], format="%d.%m.%Y")

        entries_month = search_df[(search_df["date"].dt.month == chosen_month) &
                                  (search_df["date"].dt.year == chosen_year)]

        entries_year = search_df[search_df["date"].dt.year == chosen_year]

        entries_month_cat = search_df[(search_df["date"].dt.month == chosen_month) &
                                      (search_df["date"].dt.year == chosen_year) &
                                      (search_df["category"] == chosen_cat.lower())]

        for cat in category_list:
            cat_df = search_df[search_df["category"] == cat.lower()]
            cat_sum = cat_df["price"].sum()
            cat_dict[cat] = cat_sum

        total_sum_per_month = sum(entries_month["price"])
        total_sum_per_year = sum(entries_year["price"])

        # wenn keine Kategorie gewaehlt wurde
        if not chosen_cat:
            # wenn Monat gewaehlt wurde
            if chosen_month > 0:
                total_purchases.config(text=f"Total purchases: {len(entries_month)}\n"
                                            f"Total cost: {round(total_sum_per_month, 2):.2f} EUR")

                text_label(gui_frame_2, label_to_remove, 0, chosen_month, chosen_year)

                shop_sums = entries_month.groupby("shop")["price"].sum()
                cat_sums = entries_month.groupby("category")["price"].sum()

                chart_frame = tk.Frame(gui_frame_2)
                chart_frame.grid(row=8, column=0)

                fig, ax = plt.subplots(figsize=(4, 3))

                ax.set_aspect('equal')
                ax.pie(shop_sums.values, labels=shop_sums.index, autopct="%1.1f%%", colors=color_list)
                ax.set_title(f"Shops for {chosen_month}/{chosen_year}")

                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().grid(row=8, column=0)

                chart_frame_2 = tk.Frame(gui_frame_2)
                chart_frame_2.grid(row=8, column=2)

                fig2, ax2 = plt.subplots(figsize=(4, 3))

                ax2.set_aspect('equal')

                ax2.pie(cat_sums.values, labels=cat_sums.index, autopct="%1.1f%%", colors=color_list)
                ax2.set_title(f"Categories for {chosen_month}/{chosen_year}")

                canvas_2 = FigureCanvasTkAgg(fig2, master=chart_frame_2)
                canvas_2.draw()
                canvas_2.get_tk_widget().grid(row=8, column=2)

            # wenn kein Monat gewaehlt wurde
            else:
                total_purchases.config(text=f"Total purchases: {len(entries_year)}\n"
                                            f"Total cost: {round(total_sum_per_year, 2):.2f} EUR")

                text_label(gui_frame_2, label_to_remove, 0, 0, chosen_year)

                chart_frame = tk.Frame(gui_frame_2)
                chart_frame.grid(row=8, column=0)

                shop_sums = entries_year.groupby("shop")["price"].sum()
                cat_sums = entries_year.groupby("category")["price"].sum()

                fig, ax = plt.subplots(figsize=(4, 3))

                ax.set_aspect('equal')
                ax.pie(shop_sums.values, labels=shop_sums.index, autopct="%1.1f%%", colors=color_list)
                ax.set_title(f"Shops for {chosen_year}")

                canvas = FigureCanvasTkAgg(fig, master=gui_frame_2)
                canvas.draw()
                canvas.get_tk_widget().grid(row=8, column=0)

                chart_frame_2 = tk.Frame(gui_frame_2)
                chart_frame_2.grid(row=8, column=2)

                fig2, ax2 = plt.subplots(figsize=(4, 3))

                ax2.set_aspect('equal')
                ax2.pie(cat_sums.values, labels=cat_sums.index, autopct="%1.1f%%", colors=color_list)
                ax2.set_title(f"Category for {chosen_year}")

                canvas_2 = FigureCanvasTkAgg(fig2, master=gui_frame_2)
                canvas_2.draw()
                canvas_2.get_tk_widget().grid(row=8, column=2)
        # wenn Kategorie gewaehlt wurde
        else:
            cat_df = search_df[search_df["category"] == chosen_cat]
            cat_df_month = cat_df[(cat_df["date"].dt.month == chosen_month) & (cat_df["date"].dt.year == chosen_year)]
            cat_df_year = cat_df[cat_df["date"].dt.year == chosen_year]

            # wenn Kategorie und Monat gewaehlt wurden
            if chosen_month > 0:
                cat_sums = entries_month_cat.groupby("category")["price"].sum()

                total_purchases.config(text=f"Total purchases: {len(cat_df_month)}\nTotal cost: {sum(cat_sums):.2f} EUR",
                                       font=bold_font)

                text_label(gui_frame_2, label_to_remove, chosen_cat.title(), chosen_month, current_year)

            # wenn Kategorie aber kein Monat gewaehlt wurde
            else:
                cat_sums = cat_df_year.groupby("category")["price"].sum()
                total_purchases.config(text=f"Total purchases: {len(cat_df_year)}\nTotal cost: {sum(cat_sums):.2f} EUR",
                                       font=bold_font)

                text_label(gui_frame_2, label_to_remove, chosen_cat.title(), 0, current_year)

    stats_window = tk.Toplevel(main_window)
    stats_window.minsize(900, 800)
    stats_window.config(bg="white")
    stats_window.title("PLANISTA Statistics")

    selected_month = tk.StringVar()
    selected_cat_stats = tk.StringVar()

    gui_frame_2 = tk.Frame(stats_window, bg="white")
    gui_frame_2.grid(row=0, column=0)

    logo_label_2 = tk.Label(gui_frame_2, image=logo)
    logo_label_2.grid(row=0, column=1)

    month_text = tk.Label(master=gui_frame_2, text="Month", font=font, bg="white")
    month_text.grid(row=1, column=0, pady=20)

    year_text = tk.Label(master=gui_frame_2, text="Year", font=font, bg="white")
    year_text.grid(row=1, column=1, pady=20)

    cat_text = tk.Label(master=gui_frame_2, text="Category", font=font, bg="white")
    cat_text.grid(row=1, column=2, pady=20)

    text_label(gui_frame_2, label_to_remove, 0, 0, current_year)

    month_menu = tk.OptionMenu(gui_frame_2, selected_month, *month_list)
    month_menu.config(bg=orange_color, font=font, width=2)
    month_menu.grid(row=2, column=0, padx=20)

    menu_1 = gui_frame_2.nametowidget(month_menu.menuname)
    menu_1.config(font=("open sans", 13))

    year_entry = tk.Entry(master=gui_frame_2, justify="right", font=("courier", 16), bg=paper_color)
    year_entry.grid(row=2, column=1)
    year_entry.insert(0, str(current_year))
    year_entry.bind("<Button-1>", clear_year)

    category_menu = tk.OptionMenu(gui_frame_2, selected_cat_stats, *category_list)
    category_menu.config(bg=orange_color, width=15, font=font)
    category_menu.grid(row=2, column=2, padx=30)

    menu_2 = gui_frame_2.nametowidget(category_menu.menuname)
    menu_2.config(font=("open sans", 13))

    search_button = tk.Button(master=gui_frame_2,
                              text="Search",
                              font=font,
                              command=search_stats,
                              bg=blue_color,
                              width=10
                              )
    search_button.grid(row=3, column=1, padx=20, pady=30)

    reset_button = tk.Button(master=gui_frame_2,
                             text="RESET",
                             font=font,
                             bg=red_color,
                             width=10,
                             command=reset_entries,
                             )
    reset_button.grid(row=3, column=2)

    total_purchases = tk.Label(master=gui_frame_2,
                               text=f"Total purchases: {len(overall_stats_df)}\n"
                                    f"Total cost: {overall_sum :.2f} EUR",
                               font=bold_font,
                               bg="white"
                               )
    total_purchases.grid(row=8, column=1, padx=20, pady=20)

    start_shop_sums = overall_stats_df.groupby("shop")["price"].sum()
    start_cat_sums = overall_stats_df.groupby("category")["price"].sum()

    start_frame = tk.Frame(gui_frame_2)
    start_frame.grid(row=8, column=0)

    fig, ax = plt.subplots(figsize=(4, 3))

    ax.set_aspect('equal')
    ax.pie(start_shop_sums.values, labels=start_shop_sums.index, autopct="%1.1f%%", colors=color_list)
    ax.set_title("Overall Shops")

    canvas = FigureCanvasTkAgg(fig, master=gui_frame_2)
    canvas.draw()
    canvas.get_tk_widget().grid(row=8, column=0)

    start_frame_2 = tk.Frame(gui_frame_2)
    start_frame_2.grid(row=8, column=2)

    fig2, ax2 = plt.subplots(figsize=(4, 3))

    ax2.set_aspect('equal')
    ax2.pie(start_cat_sums.values, labels=start_cat_sums.index, autopct="%1.1f%%", colors=color_list)
    ax2.set_title("Overall Categories")

    canvas_2 = FigureCanvasTkAgg(fig2, master=gui_frame_2)
    canvas_2.draw()
    canvas_2.get_tk_widget().grid(row=8, column=2)


# GUI

main_window = tk.Tk()
main_window.minsize(750, 500)
main_window.config(bg="white")
main_window.title("PLANISTA")

gui_frame = tk.Frame(main_window)
gui_frame.grid(row=0, column=0)
gui_frame.config(bg="white")

image = Image.open("logo.png")
logo = ImageTk.PhotoImage(image)

selected_category = tk.StringVar()
selected_category.set("---")

selected_shop = tk.StringVar()
selected_shop.set("---")

logo_label = tk.Label(gui_frame, image=logo)
logo_label.grid(row=0, column=2, columnspan=3, pady=20)

item_text = tk.Label(master=gui_frame, text="Item", font=font, bg="white")
item_text.grid(row=1, column=1)

cost_text = tk.Label(master=gui_frame, text="Cost", font=("open sans", 14), bg="white")
cost_text.grid(row=1, column=2)

category_text = tk.Label(master=gui_frame, text="Category", font=font, bg="white")
category_text.grid(row=1, column=4)

shop_text = tk.Label(master=gui_frame, text="Shop", font=font, bg="white")
shop_text.grid(row=1, column=3)

date_text = tk.Label(master=gui_frame, text="Date (dd.mm.yyyy)", font=font, bg="white")
date_text.grid(row=1, column=7)

last_entry_string = ""
if len(str(last_entry_price).split(".")[1]) == 1:
    last_entry_string = f"{last_entry_price}0"
print(last_entry_string)
if last_entry_item:
    last_entry_text = tk.Label(master=gui_frame,
                               text=f"Your last entry: {last_entry_item.title()} - "
                               f"{last_entry_string} EUR - "
                               f"{last_entry_date}",
                               font=font,
                               bg="white"
                               )
    last_entry_text.grid(row=4, column=2, columnspan=3)
else:
    last_entry_text = tk.Label(master=gui_frame,
                               text="",
                               font=font,
                               bg="white"
                               )
    last_entry_text.grid(row=4, column=2, columnspan=3)

item_entry = tk.Entry(master=gui_frame, justify="right", font=font, bg=paper_color)
item_entry.grid(row=2, column=1, padx=10)

cost_entry = tk.Entry(master=gui_frame, justify="right", font=("courier", 20), bg=paper_color, width=8)
cost_entry.grid(row=2, column=2)

date_entry = tk.Entry(master=gui_frame, font=("courier", 15), justify="right", bg=paper_color, width=14)
date_entry.grid(row=2, column=7, padx=10)
date_entry.insert(1, current_date)
date_entry.bind("<Button-1>", entry_klick)

save_button = tk.Button(master=gui_frame,
                        text="SAVE",
                        font=font,
                        command=save_data,
                        bg=green_color,
                        width=20,
                        )
save_button.grid(row=3, column=2, padx=20, pady=40, columnspan=3)

stats_button = tk.Button(master=gui_frame,
                         text="Statistics",
                         font=font,
                         command=open_stats_window,
                         bg=blue_color,
                         width=25,
                         )
stats_button.grid(row=5, column=2, pady=50, columnspan=3)

drop_down_cat = tk.OptionMenu(gui_frame, selected_category, *category_list)
drop_down_cat.config(bg=orange_color, font=font, width=6)
drop_down_cat.grid(row=2, column=4)

menu_3 = gui_frame.nametowidget(drop_down_cat.menuname)
menu_3.config(font=font)

drop_down_shop = tk.OptionMenu(gui_frame, selected_shop, *shop_list)
drop_down_shop.config(bg=orange_color, font=font, width=6)
drop_down_shop.grid(row=2, column=3, padx=10)

menu_4 = gui_frame.nametowidget(drop_down_shop.menuname)
menu_4.config(font=font)

chart_frame = tk.Frame(main_window)
chart_frame.grid(row=6, column=0, padx=20)

this_year_df = dataframe[dataframe["date"].dt.year == current_year]
this_years_sum = this_year_df.groupby("shop")["price"].sum()

fig, ax = plt.subplots(figsize=(5, 4))

if bad_stuff_list:
    ax.pie(bad_stuff_values,
           labels=bad_stuff_list,
           colors=color_list,
           autopct=lambda p: f'{p * sum(bad_stuff_values) / 100 :.0f} EUR')
    ax.set_title(f"Hall of Shame {current_month}/{current_year}")
else:
    ax.pie(bad_stuff_values,
           labels=bad_stuff_list,
           colors=color_list,
           autopct=lambda p: f'{p * sum(bad_stuff_values) / 100 :.0f} EUR')
    ax.set_title("")

canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.LEFT)

update_last_entry()
main_window.mainloop()
