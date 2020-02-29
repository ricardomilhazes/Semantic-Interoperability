USE exams;

CREATE TRIGGER move_to_wl
AFTER UPDATE ON exam
FOR EACH ROW
INSERT INTO worklist
SELECT NEW.idRequest,NEW.State,NEW.Date,
		NEW.Medical_Act,NEW.idUser,NEW.Report,NEW.Notes
        name,idProcess,address,mobile,notes
FROM user
WHERE NEW.idUser = user.idUser;