-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema exams
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema exams
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `exams` DEFAULT CHARACTER SET utf8 ;
USE `exams` ;

-- -----------------------------------------------------
-- Table `exams`.`Worklist`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `exams`.`Worklist` (
  `idWorkList` INT NOT NULL AUTO_INCREMENT,
  `Exam_idRequest` INT NULL,
  `State` VARCHAR(45) NULL,
  `Date` DATETIME NULL,
  `Medical_Act` VARCHAR(5) NULL,
  `User_idUser` INT NULL,
  `Name` VARCHAR(45) NULL,
  `idProcess` INT NULL,
  `Address` VARCHAR(200) NULL,
  `Mobile` VARCHAR(13) NULL,
  `Notes` VARCHAR(45) NULL,
  `Report` VARCHAR(1000) NULL,
  PRIMARY KEY (`idWorkList`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `exams`.`User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `exams`.`User` (
  `idUser` INT NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(45) NOT NULL,
  `idProcess` INT NOT NULL,
  `Address` VARCHAR(200) NOT NULL,
  `Mobile` VARCHAR(13) NOT NULL,
  PRIMARY KEY (`idUser`),
  UNIQUE INDEX `idUtente_UNIQUE` (`idUser` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `exams`.`Exam`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `exams`.`Exam` (
  `idRequest` INT NOT NULL AUTO_INCREMENT,
  `State` VARCHAR(1) NOT NULL,
  `Date` DATETIME NOT NULL,
  `Medical_Act` VARCHAR(5) NOT NULL,
  `User_idUser` INT NOT NULL,
  `Report` VARCHAR(1000) NULL,
  `Notes` VARCHAR(45) NULL,
  PRIMARY KEY (`idRequest`),
  UNIQUE INDEX `idPedidos_UNIQUE` (`idRequest` ASC) VISIBLE,
  INDEX `fk_Pedidos_Utente_idx` (`User_idUser` ASC) VISIBLE,
  CONSTRAINT `fk_Pedidos_Utente`
    FOREIGN KEY (`User_idUser`)
    REFERENCES `exams`.`User` (`idUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
