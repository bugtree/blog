-- init.sql

-- ���������ݿ⣺blog,�ͽ���ɾ��
drop database if exists blog;

-- �½����ݿ�blog
create database blog character set utf8;

-- ʹ�����ݿ�: blog
use blog;

-- �����û��������ݿ�.���Ȩ��
-- grant Ȩ��1,Ȩ��2,��Ȩ��n on ���ݿ�����.������ to �û���@�û���ַ identified by �����ӿ���;
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
