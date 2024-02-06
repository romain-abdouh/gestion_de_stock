import mysql.connector
import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askinteger
from tkinter.filedialog import asksaveasfilename
import csv

class Product:
    def __init__(self, host, user, password, database):
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.mydb.cursor()

    def add_produit(self, nom, description, prix, quantitee, id_categorie):
        query = "INSERT INTO product (name, description, price, quantity, id_category) VALUES (%s, %s, %s, %s, %s)"
        values = (nom, description, prix, quantitee, id_categorie)
        self.cursor.execute(query, values)
        self.mydb.commit()
        print("Produit ajouté avec succès!")
    
    def read_produit(self, selected_category=None):
        if selected_category:
            query = "SELECT product.id, product.name, product.description, product.price, product.quantity, category.name AS category_name FROM product JOIN category ON product.id_category = category.id WHERE category.name = %s"
            values = (selected_category,)
            self.cursor.execute(query, values)
        else:
            query = "SELECT product.id, product.name, product.description, product.price, product.quantity, category.name AS category_name FROM product JOIN category ON product.id_category = category.id"
            self.cursor.execute(query)

        result = self.cursor.fetchall()
        return result

    def update_produit(self, nouveau_prix, nouveau_quantitee, id):
        query = "UPDATE product SET price = %s, quantity = %s WHERE id = %s"
        values = (nouveau_prix, nouveau_quantitee, id)
        self.cursor.execute(query, values)
        self.mydb.commit()
        print("Produit mis à jour avec succès!")

    def delete_produit(self, produit_id):
        query = "DELETE FROM product WHERE id = %s "
        values = (produit_id,)
        self.cursor.execute(query,values)
        self.mydb.commit()
        print("Produit supprimé")
    
    def close_connection(self):
            self.cursor.close()
            self.mydb.close()


class Category:
    def __init__(self, host, user, password, database):
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.mydb.cursor()

    def add_categorie(self, nom):
        query = "INSERT INTO category (name) VALUES (%s)"
        values = (nom,)
        self.cursor.execute(query, values)
        self.mydb.commit()
        print("Categorie ajouté avec succès!")

    def get_category_id(self, category_name):
        query = "SELECT id FROM category WHERE name = %s"
        values = (category_name,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"Aucune catégorie trouvée avec le nom {category_name}.")
            return None
    
    def read_categorie(self):
        query = "SELECT name FROM category"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        if result:
            return [nom[0] for nom in result]
        else:
            print("Aucune catégorie trouvée.")
            return []

    def update_categorie(self, nouveau_nom, id):
        query = "UPDATE category SET name = %s WHERE id = %s"
        values = (nouveau_nom, id)
        self.cursor.execute(query, values)
        self.mydb.commit()
        print("categorie mis à jour avec succès!")

    def delete_categorie(self, categorie_id):
        query = "DELETE FROM category WHERE id = %s "
        values = (categorie_id,)
        self.cursor.execute(query,values)
        self.mydb.commit()
        print("categorie supprimé")

    def close_connection(self):
            self.cursor.close()
            self.mydb.close()
        
class StockGUI:
    def __init__(self, root, host, user, password, database):
        self.root = root
        self.root.title("Gestion des Stocks")
        self.root.configure(bg='grey')

        # Initialisation de gerer_produit
        self.gerer_produit = Product(host, user, password, database)
        # Initialisation de gerer_categorie
        self.gerer_categorie = Category(host, user, password, database)

        title_label = tk.Label(root, text="Gestion de Stock", bg="black", fg="white", font=("Helvetica", 20))
        title_label.pack(pady=10)

        # Création du tableau
        columns = ("ID Produit", "Nom", "Description", "Prix", "Quantité", "ID Catégorie")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(pady=20)
        self.populate_table()

        # Boutons alignés horizontalement
        add_product_button = tk.Button(root, text="Ajouter un produit", command=self.add_product_popup)
        add_product_button.pack(side='left', padx=5)

        modify_button = tk.Button(root, text="Modifier un produit", command=self.modify_product_popup)
        modify_button.pack(side='left', padx=5)

        choose_category_button = tk.Button(root, text="Choisir une catégorie", command=self.choose_category_popup)
        choose_category_button.pack(side='left', padx=5)

        delete_button = tk.Button(root, text="Supprimer un produit", command=self.delete_product)
        delete_button.pack(side='left', padx=5)

        export_button = tk.Button(root, text="Exporter en CSV", command=self.export_to_csv)
        export_button.pack(side='left', padx=5)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(pady=20)
        self.populate_table()

    def add_product_popup(self):
        # Créer une fenêtre modale pour saisir les informations du produit
        add_product_window = tk.Toplevel(self.root)
        add_product_window.title("Ajouter un produit")

        # Créer des champs de saisie et des libellés pour chaque attribut du produit
        tk.Label(add_product_window, text="Nom du produit:").pack()
        product_name_entry = tk.Entry(add_product_window)
        product_name_entry.pack()

        tk.Label(add_product_window, text="Description:").pack()
        product_description_entry = tk.Entry(add_product_window)
        product_description_entry.pack()

        tk.Label(add_product_window, text="Prix:").pack()
        product_price_entry = tk.Entry(add_product_window)
        product_price_entry.pack()

        tk.Label(add_product_window, text="Quantité:").pack()
        product_quantity_entry = tk.Entry(add_product_window)
        product_quantity_entry.pack()

        # Récupérer les catégories
        categories = self.gerer_categorie.read_categorie()
        if categories is not None:
            # Ajouter une liste déroulante pour choisir la catégorie
            tk.Label(add_product_window, text="Catégorie:").pack()
            selected_category = tk.StringVar()
            category_dropdown = ttk.Combobox(add_product_window, textvariable=selected_category, values=categories)
            category_dropdown.pack()

            # Fonction pour ajouter le produit lors du clic sur le bouton "Ajouter"
            def add_product():
                nom = product_name_entry.get()
                description = product_description_entry.get()
                prix = float(product_price_entry.get())
                quantitee = int(product_quantity_entry.get())
                selected_category_id = self.gerer_categorie.get_category_id(selected_category.get())

                self.gerer_produit.add_produit(nom, description, prix, quantitee, selected_category_id)
                self.populate_table()  # Rafraîchir le tableau après l'ajout
                add_product_window.destroy()

            # Bouton pour ajouter le produit
            add_button = tk.Button(add_product_window, text="Ajouter", command=add_product)
            add_button.pack()
        else:
            tk.Label(add_product_window, text="Aucune catégorie trouvée.").pack()

            # Bouton pour ajouter le produit
            add_button = tk.Button(add_product_window, text="Ajouter", command=add_product)
            add_button.pack()

    def modify_product_popup(self):
        # Créer une fenêtre modale pour saisir les informations du produit à modifier
        modify_product_window = tk.Toplevel(self.root)
        modify_product_window.title("Modifier un produit")

        # Créer des champs de saisie et des libellés pour chaque attribut du produit
        tk.Label(modify_product_window, text="ID du produit à modifier:").pack()
        product_id_entry = tk.Entry(modify_product_window)
        product_id_entry.pack()

        tk.Label(modify_product_window, text="Nouveau prix:").pack()
        new_price_entry = tk.Entry(modify_product_window)
        new_price_entry.pack()

        tk.Label(modify_product_window, text="Nouvelle quantité:").pack()
        new_quantity_entry = tk.Entry(modify_product_window)
        new_quantity_entry.pack()

        # Fonction pour modifier le produit lors du clic sur le bouton "Modifier"
        def modify_product():
            try:
                product_id = int(product_id_entry.get())
                new_price = float(new_price_entry.get())
                new_quantity = int(new_quantity_entry.get())

                # Appel à la méthode update_produit pour effectuer la modification
                self.gerer_produit.update_produit(new_price, new_quantity, product_id)
                self.populate_table()  # Rafraîchir le tableau après la modification
                modify_product_window.destroy()

            except ValueError:
                tk.messagebox.showerror("Erreur", "Veuillez saisir des valeurs numériques valides.")

        # Bouton pour modifier le produit
        modify_button = tk.Button(modify_product_window, text="Modifier", command=modify_product)
        modify_button.pack()
    
    def delete_product(self):
        # Boîte de dialogue pour saisir l'ID du produit à supprimer
        product_id = askinteger("Supprimer un produit", "Entrez l'ID du produit à supprimer:")

        if product_id is not None:
            # Appeler la méthode delete_produit pour supprimer le produit
            self.gerer_produit.delete_produit(product_id)
            self.populate_table()  # Rafraîchir le tableau après la suppression

    def choose_category_popup(self):
        # Créer une fenêtre modale pour choisir la catégorie
        choose_category_window = tk.Toplevel(self.root)
        choose_category_window.title("Choisir une catégorie")

        # Récupérer les catégories depuis la base de données
        categories = self.gerer_categorie.read_categorie()

        if categories:
            # Ajouter une liste déroulante pour choisir la catégorie
            tk.Label(choose_category_window, text="Sélectionner une catégorie:").pack()
            selected_category = tk.StringVar()
            category_dropdown = ttk.Combobox(choose_category_window, textvariable=selected_category, values=categories)
            category_dropdown.pack()

            # Bouton pour appliquer le filtre par catégorie
            apply_button = tk.Button(choose_category_window, text="Appliquer", command=lambda: self.filter_by_category(selected_category.get()))
            apply_button.pack()
        else:
            tk.Label(choose_category_window, text="Aucune catégorie trouvée.").pack()

    def filter_by_category(self, selected_category):
        # Efface le contenu actuel du tableau
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Récupère les données depuis la base de données pour la catégorie sélectionnée
        produits = self.gerer_produit.read_produit(selected_category)

        # Vérifie si des produits ont été récupérés
        if produits:
            # Remplit le tableau avec les données
            for produit in produits:
                self.tree.insert("", "end", values=produit)
        else:
            tk.messagebox.showinfo("Information", "Aucun produit trouvé pour cette catégorie.")

    def export_to_csv(self):
        # Récupère les données depuis la base de données
        produits = self.gerer_produit.read_produit()

        if produits is not None:
            # Demande à l'utilisateur l'emplacement pour sauvegarder le fichier CSV
            file_path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

            if file_path:
                try:
                    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
                        # Utilise le module CSV pour écrire les données dans le fichier
                        csv_writer = csv.writer(csvfile)
                        
                        # Écrit les en-têtes
                        headers = ["ID Produit", "Nom", "Description", "Prix", "Quantité", "ID Catégorie"]
                        csv_writer.writerow(headers)

                        # Écrit les données
                        for produit in produits:
                            csv_writer.writerow(produit)

                    print(f"Données exportées avec succès vers : {file_path}")

                except Exception as e:
                    print(f"Erreur lors de l'exportation : {e}")
            else:
                print("L'emplacement du fichier n'a pas été spécifié.")
        
    def populate_table(self):
        # Efface le contenu actuel du tableau
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Récupère les données depuis la base de données
        produits = self.gerer_produit.read_produit()

        # Vérifie si des produits ont été récupérés
        if produits is not None:
            # Remplit le tableau avec les données
            for produit in produits:
                self.tree.insert("", "end", values=produit)


    

host = "localhost"
user = "root"
password = "Ultrasmars1379!"
database = "store"

mydb = mysql.connector.connect(
    host = host,
    user = user,
    password = password,
    database = database
)

gerer_produit = Product(host, user, password, database)

gerer_produit.read_produit()

gerer_categorie = Category(host, user, password, database)

gerer_categorie.read_categorie()

root = tk.Tk()
app = StockGUI(root, host, user, password, database)
root.mainloop()

app.gerer_produit.close_connection()
gerer_produit.close_connection()
gerer_categorie.close_connection()