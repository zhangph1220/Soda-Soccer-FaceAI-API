from app import db


class faces_info(db.Model):
    '''
    faces_info表格(人脸特征表格):
    '''
    __tablename__ = 'faces_info'
    __table_args__ = (
        db.PrimaryKeyConstraint('play_ifcoach', 'play_id', 'play_name', 'club_id', 'season', 'comp_id'),
    )

    play_ifcoach = db.Column(db.Integer, unique = False)
    play_id = db.Column(db.Integer, unique = False)
    play_name = db.Column(db.String(60), unique = False)
    club_id = db.Column(db.Integer, unique = False)
    season = db.Column(db.String(20), unique = False)
    comp_id = db.Column(db.Integer, unique = False)
    pic_path = db.Column(db.String(100), unique = False)

    def __repr__(self):
        return '<No.%r Image name: %r>\n' % (self.play_id, self.play_name)