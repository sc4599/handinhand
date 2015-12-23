/*
Navicat MySQL Data Transfer

Source Server         : 本机
Source Server Version : 50625
Source Host           : 192.168.1.18:3306
Source Database       : handinhand

Target Server Type    : MYSQL
Target Server Version : 50625
File Encoding         : 65001

Date: 2015-12-21 15:45:54
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for comment
-- ----------------------------
DROP TABLE IF EXISTS `comment`;
CREATE TABLE `comment` (
  `comment_id` int(11) NOT NULL AUTO_INCREMENT,
  `patient_tel` varchar(11) DEFAULT NULL,
  `patient_name` varchar(50) DEFAULT NULL,
  `doctor_tel` varchar(11) DEFAULT NULL,
  `doctor_name` varchar(50) DEFAULT NULL,
  `comment_content` varchar(2000) DEFAULT NULL,
  `comment_datetime` datetime DEFAULT NULL,
  `grade` double(4,0) DEFAULT NULL,
  `comment_pic` varchar(1000) DEFAULT NULL COMMENT '评论照片，是一个json 集合， 里面可能有一张或多张评论照片的图片地址。',
  PRIMARY KEY (`comment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of comment
-- ----------------------------

-- ----------------------------
-- Table structure for detailtask
-- ----------------------------
DROP TABLE IF EXISTS `detailtask`;
CREATE TABLE `detailtask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `symptom` varchar(200) DEFAULT NULL,
  `datetime` datetime DEFAULT NULL,
  `lat` varchar(50) DEFAULT NULL,
  `lon` varchar(50) DEFAULT NULL,
  `patient_tel` varchar(11) DEFAULT NULL,
  `patient_name` varchar(50) DEFAULT NULL,
  `doctor_tel` varchar(11) DEFAULT NULL,
  `doctor_name` varchar(50) DEFAULT NULL,
  `comment_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
-- Table structure for handinhand_doctor
-- ----------------------------
DROP TABLE IF EXISTS `handinhand_doctor`;
CREATE TABLE `handinhand_doctor` (
  `tel` varchar(11) NOT NULL,
  `password` varchar(50) NOT NULL,
  `age` varchar(3) NOT NULL,
  `pic` varchar(200) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `gender` varchar(1) DEFAULT NULL,
  `collection_count` int(4) DEFAULT NULL,
  `treatment_count` int(4) DEFAULT NULL,
  `qualifications_pic` varchar(200) DEFAULT NULL,
  `identification_pic` varchar(200) DEFAULT NULL,
  `hospital` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`tel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of handinhand_doctor
-- ----------------------------

-- ----------------------------
-- Table structure for handinhand_patient
-- ----------------------------
DROP TABLE IF EXISTS `handinhand_patient`;
CREATE TABLE `handinhand_patient` (
  `tel` varchar(11) NOT NULL,
  `password` varchar(50) NOT NULL,
  `pic` varchar(255) DEFAULT NULL,
  `name` varchar(50) NOT NULL,
  `gender` varchar(1) NOT NULL,
  `age` varchar(3) DEFAULT NULL,
  `treatment_count` int(4) DEFAULT NULL,
  `collection_list_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`tel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of handinhand_patient
-- ----------------------------
