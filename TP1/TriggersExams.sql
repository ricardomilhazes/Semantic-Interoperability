USE exams;

CREATE TRIGGER move_to_wl
AFTER UPDATE ON exam
FOR EACH ROW
INSERT INTO worklist 
SELECT NULL,NEW.idRequest,NEW.State,NEW.Date,
		NEW.Medical_Act,NEW.User_idUser,Name,idProcess,
        Address,Mobile,NEW.Notes,NEW.Report
FROM user
WHERE NEW.User_idUser = user.idUser;