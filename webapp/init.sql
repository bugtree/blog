-- init.sql

-- 若存在数据库：blog,就将其删除
drop database if exists blog;

-- 新建数据库blog
create database blog character set utf8;

-- 使用数据库: blog
use blog;

-- 赋予用户操作数据库.表的权限
-- grant 权限1,权限2,…权限n on 数据库名称.表名称 to 用户名@用户地址 identified by ‘连接口令;
grant select, insert, update, delete on blog.* to 'bugtree'@'localhost' identified by 'bugtree';


create table users(
    `id` varchar(50) not null,
    `email` varchar(50) not null,
    `password` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `image` varchar(500) not null,
    `created_at` real not null,
    unique key `idx_email` (`email`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table blogs (
    `id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `name` varchar(50) not null,
    `summary` varchar(200) not null,
    `content` text not null,
    `view_count` int unsigned not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)

) engine=innodb default charset=utf8;

create table comments (
    `id` varchar(50) not null,
    `blog_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `content` text not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;
