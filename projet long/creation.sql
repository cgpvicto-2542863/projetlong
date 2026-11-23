DROP DATABASE IF EXISTS pizzeria;
CREATE DATABASE pizzeria;
USE pizzeria;


CREATE TABLE croutes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom_croute VARCHAR(50) NOT NULL
);

CREATE TABLE sauces (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom_sauce VARCHAR(50) NOT NULL
);

CREATE TABLE garnitures (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom_garniture VARCHAR(50) NOT NULL
);

CREATE TABLE clients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    adresse_livraison VARCHAR(255) NOT NULL
);

CREATE TABLE commandes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_client INT NOT NULL,
    date_commande DATETIME NOT NULL,
    FOREIGN KEY (id_client) REFERENCES clients(id)
);

CREATE TABLE pizza (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_commande INT NOT NULL,
    id_croute INT NOT NULL,
    id_sauce INT NOT NULL,
    FOREIGN KEY (id_commande) REFERENCES commandes(id) ON DELETE CASCADE,
    FOREIGN KEY (id_croute) REFERENCES croutes(id),
    FOREIGN KEY (id_sauce) REFERENCES sauces(id)
);

CREATE TABLE pizza_garniture (
    id_pizza INT NOT NULL,
    id_garniture INT NOT NULL,
    PRIMARY KEY (id_pizza, id_garniture),
    FOREIGN KEY (id_pizza) REFERENCES pizza(id) ON DELETE CASCADE,
    FOREIGN KEY (id_garniture) REFERENCES garnitures(id)
);

CREATE TABLE commandes_en_attente (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_commande INT NOT NULL,
    FOREIGN KEY (id_commande) REFERENCES commandes(id) ON DELETE CASCADE
);


DELIMITER //
CREATE TRIGGER trg_commande_en_attente
AFTER INSERT ON commandes
FOR EACH ROW
BEGIN
    INSERT INTO commandes_en_attente (id_commande) VALUES (NEW.id);
END//

CREATE TRIGGER trg_max_garnitures
BEFORE INSERT ON pizza_garniture
FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*) FROM pizza_garniture WHERE id_pizza = NEW.id_pizza) >= 4 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Une pizza ne peut pas avoir plus de 4 garnitures';
    END IF;
END//
DELIMITER ;