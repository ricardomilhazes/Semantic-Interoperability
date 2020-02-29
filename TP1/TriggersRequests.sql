USE requests;

CREATE TRIGGER move_to_wl
AFTER INSERT ON request
FOR EACH ROW
INSERT INTO worklist
SELECT NEW.idRequest,NEW.State,NEW.Date,
		NEW.Medical_Act,NEW.idUser,name,idProcess,
		address,mobile,notes
FROM user
WHERE NEW.idUser = user.idUser;


