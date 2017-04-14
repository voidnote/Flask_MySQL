-- SELECT first_name, last_name, message, DATE_FORMAT(messages.created_at, '%M %D %Y') as date 
-- FROM messages
-- JOIN users ON messages.user_id = users.id
-- 
-- SELECT *
-- FROM comments

select * from messages

SELECT * FROM comments

SELECT * 
FROM users
JOIN messages ON messages.user_id = users.id
JOIN comments ON comments.message_id = messages.id

SELECT comments.id, CONCAT(first_name , " ", last_name), comments, DATE_FORMAT(comments.created_at, '%M %D %Y') as date 
FROM comments 
JOIN users ON comments.user_id = users.id
JOIN messages ON messages.id = comments.message_id
