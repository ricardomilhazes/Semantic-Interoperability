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
-- Table `exams`.`MessageHL7`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `exams`.`MessageHL7` (
  `idMessageHL7` INT NOT NULL,
  `Message` TEXT NULL,
  PRIMARY KEY (`idMessageHL7`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
