-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jun 05, 2025 at 12:02 AM
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
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
CREATE TABLE IF NOT EXISTS `accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `account_name` varchar(100) NOT NULL,
  `account_type` varchar(50) NOT NULL,
  `balance` decimal(12,2) DEFAULT '0.00',
  `account_number` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`id`, `user_id`, `account_name`, `account_type`, `balance`, `account_number`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 1, 'Main Debit Card', 'debit_card', 1131.79, '9131', 1, '2025-05-28 06:01:32', '2025-05-28 06:01:32'),
(2, 1, 'Credit Card', 'credit_card', 241.22, '1144', 1, '2025-05-28 06:01:32', '2025-05-28 06:01:32'),
(3, 1, 'Savings Account', 'savings', 13.56, '2376', 1, '2025-05-28 06:01:32', '2025-05-28 06:01:32'),
(4, 9, 'Main Account', 'checking', 1000.00, '1234', 1, '2025-05-28 06:58:36', '2025-05-28 06:58:36');

-- --------------------------------------------------------

--
-- Table structure for table `budgets`
--

DROP TABLE IF EXISTS `budgets`;
CREATE TABLE IF NOT EXISTS `budgets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `category_id` int DEFAULT NULL,
  `budget_type` varchar(20) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `period_start` date NOT NULL,
  `period_end` date NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `category_id` (`category_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `budgets`
--

INSERT INTO `budgets` (`id`, `user_id`, `category_id`, `budget_type`, `amount`, `period_start`, `period_end`, `is_active`, `created_at`) VALUES
(1, 1, NULL, 'monthly', 5000.00, '2024-01-01', '2024-01-31', 1, '2025-05-28 06:03:58');

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `icon` varchar(50) DEFAULT 'fas fa-shopping-cart',
  `color` varchar(7) DEFAULT '#6366f1',
  `budget_limit` decimal(10,2) DEFAULT '0.00',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id`, `user_id`, `name`, `icon`, `color`, `budget_limit`, `is_active`, `created_at`) VALUES
(1, 1, 'Food & Dining', 'fas fa-utensils', '#ef4444', 800.00, 1, '2025-05-28 06:01:07'),
(2, 1, 'Transportation', 'fas fa-car', '#3b82f6', 500.00, 1, '2025-05-28 06:01:07'),
(3, 1, 'Entertainment', 'fas fa-film', '#8b5cf6', 300.00, 1, '2025-05-28 06:01:07'),
(4, 1, 'Bills & Utilities', 'fas fa-file-invoice', '#f59e0b', 1200.00, 1, '2025-05-28 06:01:07'),
(5, 1, 'Shopping', 'fas fa-shopping-bag', '#10b981', 600.00, 1, '2025-05-28 06:01:07'),
(6, 1, 'Health & Fitness', 'fas fa-heartbeat', '#ec4899', 400.00, 1, '2025-05-28 06:01:07'),
(7, 9, 'Rent & Housing', 'fas fa-home', '#f59e0b', 1200.00, 1, '2025-05-28 06:58:20');

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
  KEY `userid` (`userid`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `expenses`
--

INSERT INTO `expenses` (`id`, `userid`, `date`, `expensename`, `amount`, `paymode`, `category`, `account_id`) VALUES
(6, 9, '2025-05-28 04:17:00', 'Regional Maritime University Fees', 9000, 'onlinebanking', 'education', NULL),
(9, 9, '2025-05-28 08:44:00', 'food', 200, 'debitcard', 'food', NULL),
(1, 2, '2025-12-12 12:12:00', 'car', 1234, 'creditcard', 'entertainment', NULL),
(2, 5, '0000-00-00 00:00:00', '', 0, 'Pay-Mode', 'Category', NULL),
(3, 5, '2025-05-14 20:08:00', 'car', 180000, 'debitcard', 'other', NULL),
(4, 5, '2025-05-14 20:08:00', 'car', 180000, 'debitcard', 'other', NULL),
(10, 2, '2025-12-12 12:12:00', 'car', 1234, 'creditcard', 'entertainment', NULL),
(11, 5, '0000-00-00 00:00:00', '', 0, 'Pay-Mode', 'Category', NULL),
(12, 5, '2025-05-14 20:08:00', 'car', 180000, 'debitcard', 'other', NULL),
(13, 5, '2025-05-14 20:08:00', 'car', 180000, 'debitcard', 'other', NULL),
(14, 6, '2025-05-21 15:47:00', 'car', 123, 'cash', 'food', NULL),
(15, 8, '2025-05-28 12:12:00', 'food', 50, 'creditcard', 'food', 1),
(16, 12, '2025-05-30 12:12:00', 'food', 50000, 'creditcard', 'food', 1);

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
-- Table structure for table `profiles`
--

DROP TABLE IF EXISTS `profiles`;
CREATE TABLE IF NOT EXISTS `profiles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `age` int DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `register`
--

INSERT INTO `register` (`id`, `username`, `email`, `password`) VALUES
(13, 'Shurface123', 'lovelacejohnkwakubaidoo@gmail.com', 'scrypt:32768:8:1$pjWNrLg8pXkT86Di$79ebdc2b90d18fba5eeb160d81e8109886a0138ad71b2d99706525a7d6996298c3ba7d5c664012a7b300953a798027e85ce99c3eeee2abd26ab00620bae2198b');

-- --------------------------------------------------------

--
-- Table structure for table `savings_goals`
--

DROP TABLE IF EXISTS `savings_goals`;
CREATE TABLE IF NOT EXISTS `savings_goals` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `goal_name` varchar(100) NOT NULL,
  `target_amount` decimal(12,2) NOT NULL,
  `current_amount` decimal(12,2) DEFAULT '0.00',
  `target_date` date DEFAULT NULL,
  `description` text,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `savings_goals`
--

INSERT INTO `savings_goals` (`id`, `user_id`, `goal_name`, `target_amount`, `current_amount`, `target_date`, `description`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 1, 'Emergency Fund', 10000.00, 6800.00, '2024-12-31', NULL, 1, '2025-05-28 06:02:00', '2025-05-28 06:02:00');

-- --------------------------------------------------------

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
CREATE TABLE IF NOT EXISTS `settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `preferred_currency` enum('USD','EUR','JPY','GBP','CNY','CHF','GHC') DEFAULT 'USD',
  `dark_mode` tinyint(1) DEFAULT '0',
  `notifications_enabled` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
CREATE TABLE IF NOT EXISTS `transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `account_id` int DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `transaction_type` varchar(20) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `description` text NOT NULL,
  `merchant` varchar(100) DEFAULT NULL,
  `transaction_date` date NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `account_id` (`account_id`),
  KEY `category_id` (`category_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`id`, `user_id`, `account_id`, `category_id`, `transaction_type`, `amount`, `description`, `merchant`, `transaction_date`, `created_at`, `updated_at`) VALUES
(1, 1, 1, 3, 'expense', 10.67, 'Monthly subscription', 'Dribbble', '2024-01-08', '2025-05-28 06:04:16', '2025-05-28 06:04:16'),
(2, 1, 2, 3, 'expense', 12.01, 'Streaming service', 'Netflix', '2024-01-07', '2025-05-28 06:04:16', '2025-05-28 06:04:16'),
(3, 1, 1, 2, 'expense', 112.43, 'Accommodation booking', 'Airbnb', '2024-01-05', '2025-05-28 06:04:16', '2025-05-28 06:04:16'),
(4, 1, 2, 3, 'expense', 16.00, 'Social media subscription', 'X Subscribe', '2024-01-05', '2025-05-28 06:04:16', '2025-05-28 06:04:16');

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

-- --------------------------------------------------------

--
-- Table structure for table `user_preferences`
--

DROP TABLE IF EXISTS `user_preferences`;
CREATE TABLE IF NOT EXISTS `user_preferences` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `email_notifications` tinyint(1) DEFAULT '1',
  `budget_alerts` tinyint(1) DEFAULT '1',
  `dark_mode` tinyint(1) DEFAULT '0',
  `auto_categorization` tinyint(1) DEFAULT '1',
  `default_currency` varchar(3) DEFAULT 'GHS',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_profiles`
--

DROP TABLE IF EXISTS `user_profiles`;
CREATE TABLE IF NOT EXISTS `user_profiles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `bio` text,
  `currency` varchar(10) DEFAULT 'GHS',
  `date_format` varchar(20) DEFAULT 'DD/MM/YYYY',
  `avatar_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_profile` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
