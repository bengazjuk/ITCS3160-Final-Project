-- Replace this by the SQL code needed to create your database

CREATE TABLE items (
	item_id		 SERIAL,
	item_name		 VARCHAR(512),
	minimum_price	 FLOAT(8),
	auctions_auction_id	 INTEGER NOT NULL,
	sellers_users_user_id BIGINT NOT NULL,
	PRIMARY KEY(item_id)
);

CREATE TABLE sellers (
	seller_name	 VARCHAR(512),
	users_user_id BIGINT,
	PRIMARY KEY(users_user_id)
);

CREATE TABLE buyers (
	buyer_name	 VARCHAR(512),
	users_user_id BIGINT,
	PRIMARY KEY(users_user_id)
);

CREATE TABLE bids (
	bid_id		 SERIAL,
	bid_amount		 FLOAT(8),
	bid_time		 TIMESTAMP,
	items_item_id	 INTEGER NOT NULL,
	buyers_users_user_id BIGINT NOT NULL,
	PRIMARY KEY(bid_id)
);

CREATE TABLE auctions (
	auction_id SERIAL,
	title	 VARCHAR(512),
	description VARCHAR(512),
	end_time	 TIMESTAMP,
	status	 VARCHAR(512),
	PRIMARY KEY(auction_id)
);

CREATE TABLE auction_board (
	auction_message_id	 SERIAL,
	message_description VARCHAR(512),
	auctions_auction_id INTEGER NOT NULL,
	PRIMARY KEY(auction_message_id)
);

CREATE TABLE message_box (
	message_id		 SERIAL,
	message_description VARCHAR(512),
	users_user_id	 BIGINT NOT NULL,
	PRIMARY KEY(message_id)
);

CREATE TABLE users (
	user_id	 SERIAL,
	username VARCHAR(512),
	password VARCHAR(512),
	email	 VARCHAR(512),
	role	 VARCHAR(512),
	PRIMARY KEY(user_id)
);

CREATE TABLE notifications (
	notification_id	 SERIAL,
	message__content	 VARCHAR(1024),
	notification_type VARCHAR(512),
	sender_user_id	 BIGINT,
	receiver_user_id	 BIGINT,
	notification_time TIMESTAMP,
	is_read		 BOOL,
	users_user_id	 BIGINT NOT NULL,
	PRIMARY KEY(notification_id)
);

ALTER TABLE items ADD CONSTRAINT items_fk1 FOREIGN KEY (auctions_auction_id) REFERENCES auctions(auction_id);
ALTER TABLE items ADD CONSTRAINT items_fk2 FOREIGN KEY (sellers_users_user_id) REFERENCES sellers(users_user_id);
ALTER TABLE sellers ADD CONSTRAINT sellers_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
ALTER TABLE buyers ADD CONSTRAINT buyers_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
ALTER TABLE bids ADD CONSTRAINT bids_fk1 FOREIGN KEY (items_item_id) REFERENCES items(item_id);
ALTER TABLE bids ADD CONSTRAINT bids_fk2 FOREIGN KEY (buyers_users_user_id) REFERENCES buyers(users_user_id);
ALTER TABLE auction_board ADD CONSTRAINT auction_board_fk1 FOREIGN KEY (auctions_auction_id) REFERENCES auctions(auction_id);
ALTER TABLE message_box ADD CONSTRAINT message_box_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
ALTER TABLE notifications ADD CONSTRAINT notifications_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);


INSERT INTO USERS VALUES (100, 'buyer1','password1', 'buyer1@gmail.com', 'Buyer');
INSERT INTO USERS VALUES (200, 'seller1','password2','seller1@gmail.com', 'Seller');
INSERT INTO USERS VALUES (300, 'buyer2','password3','buyer2@gmail.com', 'Buyer');
INSERT INTO USERS VALUES (400, 'seller2','password4','seller2@gmail.com', 'Seller');

COMMIT;

