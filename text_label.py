import tkinter as tk

font = ("open sans", 18, "bold")


def text_label(root, to_remove, cat, month, year):
    # when only the year is chosen
    if cat == 0 and month == 0:
        chosen_year_text = tk.Label(master=root,
                                    text=f"Money spend in:\n{year}",
                                    font=font,
                                    bg="white"
                                    )
        chosen_year_text.grid(row=4, column=1, pady=10, sticky="s")
        to_remove.append(chosen_year_text)

    elif cat != 0 and month != 0:
        chosen_year_text = tk.Label(master=root,
                                    text=f"Money spend on {cat} in:\n{month}/{year}",
                                    font=font,
                                    bg="white"
                                    )
        chosen_year_text.grid(row=4, column=1, pady=10, sticky="s")
        to_remove.append(chosen_year_text)

    # when category was chosen
    elif cat != 0:
        chosen_year_text = tk.Label(master=root,
                                    text = f"Money spend on:\n{cat.title()}",
                                    font=font,
                                    bg="white"
                                    )
        chosen_year_text.grid(row=4, column=1, pady=10, sticky="s")
        to_remove.append(chosen_year_text)
    # when month and year chosen
    elif month != 0:
        chosen_year_text = tk.Label(master=root,
                                    text=f"Money spend in:\n{month}/{year}",
                                    font=font,
                                    bg="white"
                                    )
        chosen_year_text.grid(row=4, column=1, pady=10, sticky="s")
        to_remove.append(chosen_year_text)
