-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jun 04, 2025 at 09:32 AM
-- Server version: 9.1.0
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `expense_tracker`
--

-- --------------------------------------------------------

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
CREATE TABLE IF NOT EXISTS `expenses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userid` int NOT NULL,
  `date` datetime NOT NULL,
  `expensename` varchar(100) DEFAULT NULL,
  `amount` float DEFAULT NULL,
  `paymode` varchar(50) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `account_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `idx_expenses_userid_date` (`userid`,`date`)
) ENGINE=MyISAM AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `expenses`
--

INSERT INTO `expenses` (`id`, `userid`, `date`, `expensename`, `amount`, `paymode`, `category`, `account_id`) VALUES
(1, 2, '2025-12-12 12:12:00', 'car', 1234, 'creditcard', 'entertainment', NULL),
(2, 5, '0000-00-00 00:00:00', '', 0, 'Pay-Mode', 'Category', NULL),
(3, 5, '2025-05-14 20:08:00', 'car', 180000, 'debitcard', 'other', NULL),
(4, 5, '2025-05-14 20:08:00', 'car', 180000, 'debitcard', 'other', NULL),
(6, 6, '2025-05-21 15:47:00', 'car', 123, 'cash', 'food', NULL),
(8, 8, '2025-05-28 12:12:00', 'food', 50, 'creditcard', 'food', 1),
(19, 12, '2025-05-30 12:12:00', 'food', 50000, 'creditcard', 'food', 1);

-- --------------------------------------------------------

--
-- Table structure for table `limits`
--

DROP TABLE IF EXISTS `limits`;
CREATE TABLE IF NOT EXISTS `limits` (
  `id` int NOT NULL AUTO_INCREMENT,
  `limits` float DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `limits`
--

INSERT INTO `limits` (`id`, `limits`, `user_id`) VALUES
(1, 12, 2000),
(2, 12, 400000),
(3, 12, 200),
(4, 12, 12293),
(5, 12, 2000),
(6, 12, 300);

-- --------------------------------------------------------

--
-- Table structure for table `limitss`
--

DROP TABLE IF EXISTS `limitss`;
CREATE TABLE IF NOT EXISTS `limitss` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `limits` decimal(10,2) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_limitss_userid` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `limitss`
--

INSERT INTO `limitss` (`id`, `user_id`, `limits`, `created_at`) VALUES
(1, 12, 200.00, '2025-05-30 16:37:12');

-- --------------------------------------------------------

--
-- Table structure for table `payment_methods`
--

DROP TABLE IF EXISTS `payment_methods`;
CREATE TABLE IF NOT EXISTS `payment_methods` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `type` varchar(50) NOT NULL,
  `name` varchar(100) NOT NULL,
  `balance` decimal(10,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_payment_methods_userid` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `payment_methods`
--

INSERT INTO `payment_methods` (`id`, `user_id`, `type`, `name`, `balance`, `created_at`) VALUES
(4, 8, 'card', 'Credit Card', 1000.00, '2025-05-28 19:56:07'),
(5, 8, 'card', 'Credit Card', 1000.00, '2025-05-28 20:01:09'),
(14, 12, 'card', 'Credit Card', 1000.00, '2025-05-29 10:32:11');

-- --------------------------------------------------------

--
-- Table structure for table `register`
--

DROP TABLE IF EXISTS `register`;
CREATE TABLE IF NOT EXISTS `register` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `register`
--

INSERT INTO `register` (`id`, `username`, `email`, `password`) VALUES
(9, 'newuser', 'newestgee2@gmail.com', 'scrypt:32768:8:1$Wp7AI8Tp8fMcJZZO$d8a8055f7d0acd019367fa0bc724147d838ceb43155a72501f3131c131b14e0811'),
(12, 'eltonmorden', 'eltonmorden029@gmail.com', '123456789');

-- --------------------------------------------------------

--
-- Table structure for table `user_accounts`
--

DROP TABLE IF EXISTS `user_accounts`;
CREATE TABLE IF NOT EXISTS `user_accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userid` int NOT NULL,
  `account_name` varchar(100) NOT NULL,
  `account_type` enum('card','cash') NOT NULL,
  `balance` decimal(10,2) DEFAULT '0.00',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_accounts_userid` (`userid`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `user_accounts`
--

INSERT INTO `user_accounts` (`id`, `userid`, `account_name`, `account_type`, `balance`, `created_at`) VALUES
(1, 8, 'Credit Card', 'card', 1000.00, '2025-05-28 19:56:07'),
(2, 8, 'Credit Card', 'card', 1000.00, '2025-05-28 20:01:09'),
(11, 12, 'Credit Card', 'card', 1000.00, '2025-05-29 10:32:11');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
