USE requests;

CREATE TRIGGER move_to_wl
AFTER INSERT ON request
FOR EACH ROW
INSERT INTO worklist
SELECT NULL,NEW.idRequest,NEW.State,NEW.Date,
		NEW.Medical_Act,NEW.idUser,Name,idProcess,
		Address,Mobile,NEW.Notes,NEW.Report
FROM user
WHERE NEW.idUser = user.idUser;