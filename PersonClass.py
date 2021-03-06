import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import select, update, delete
from sqlalchemy.sql import expression
from datetime import timedelta
import json
from os import environ
from datetime import date, datetime

app = Flask(__name__)
rds_password = 'spm:spmteam09@spm-database-1.cujkm1zfxmqs.us-east-2.rds.amazonaws.com'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://' + rds_password + ':3306/LearnerSystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/LearnerSystem'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
db = SQLAlchemy(app)
CORS(app)


class Person(db.Model):
    __tableName__ = 'Person'
    __mapper_args__ = {'polymorphic_identity': 'Person'}
    PersonID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    NRIC = db.Column(db.String(100), nullable=False)
    ContactNo = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100),nullable=False)
    #__mapper_args__ = {'polymorphic_on': PersonID}

    def __init__(self, PersonID, name, NRIC,ContactNo,email):
        self.PersonID = PersonID
        self.name = name
        self.NRIC = NRIC
        self.ContactNo = ContactNo
        self.email = email

    # def json(self):
    #     return {'PersonID': self.PersonID,'name': self.name,'NRIC': self.NRIC,'ContactNo': self.ContactNo,'email': self.ContactNo}
    def json(self):
        return{
            'PersonID': self.PersonID,
            'name': self.name,
            'NRIC': self.NRIC,
            'ContactNo': self.ContactNo,
            'Email': self.email
        }
        # dataTable['TrainerList'] = []
        # for element in self.TrainerList:
        #     dataTable['TrainerList'].append(element.json())
        # return dataTable

class Trainer(Person):
    __tableName__ = 'Trainer'
    __mapper_args__ = {'polymorphic_identity': 'Trainer'}
    PersonID = db.Column(db.ForeignKey(Person.PersonID), nullable=False)
    TrainerID = db.Column(db.Integer, primary_key=True)


    def __init__(self, PersonID, TrainerID):
        self.PersonID = PersonID
        self.TrainerID = TrainerID
    #Trainer = db.relationship('Person', primaryjoin='trainer.PersonID == person.PersonID', backref='person')
    Person = db.relationship(Person, backref='trainer')
        
    def json(self):
        return {'TrainerID': self.TrainerID,'PersonID': self.PersonID}

class Learner(Person):
    __tableName__ = 'Learner'
    __mapper_args__ = {'polymorphic_identity': 'Learner'}
    PersonID = db.Column(db.ForeignKey(Person.PersonID), nullable=False, primary_key=False)
    LearnerID = db.Column(db.Integer, primary_key=True)
  
    def __init__(self, PersonID, LearnerID):
        self.PersonID = PersonID
        self.LearnerID = LearnerID

    #Learner = db.relationship('Learner', primaryjoin='learner.PersonID == person.PersonID', backref='person')
    Person = db.relationship(Person, backref='learner')

    def json(self):
        return {'LearnerID': self.LearnerID, 'PersonID':self.PersonID}


class CourseOverview(db.Model):
    __tableName__ = 'CourseOverview'
    __mapper_args__ = {'polymorphic_identity': 'CourseOverview'}
    CourseID = db.Column(db.Integer, primary_key=True)
    CourseName = db.Column(db.String(100), nullable=False)
    CourseDescription = db.Column(db.String(10000), nullable=False)
    Prerequisite = db.Column(db.Boolean, nullable=False)

    def __init__(self, CourseID, CourseName,CourseDescription,Prerequisite ):
        self.CourseID = CourseID
        self.CourseName = CourseName
        self.CourseDescription = CourseDescription
        self.Prerequisite = Prerequisite

    def json(self):
        return {'CourseID': self.CourseID, 'CourseName':self.CourseName , 'CourseDescription':self.CourseDescription ,'Prerequisite':self.Prerequisite }

class CoursePrerequisite(db.Model):
    __tableName__ = 'CoursePrerequisite'
    __mapper_args__ = {'polymorphic_identity': 'CoursePrerequisite'}
    MainCourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False, primary_key=True)
    PrerequisiteCourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False, primary_key=True)

    def __init__(self, MainCourseID, PrerequisiteCourseID):
        self.MainCourseID = MainCourseID
        self.PrerequisiteCourseID = PrerequisiteCourseID
    
    CourseOverview = db.relationship('CourseOverview', primaryjoin='CoursePrerequisite.MainCourseID == CourseOverview.CourseID', backref='CoursePrerequisite')
    CourseOverview = db.relationship('CourseOverview', primaryjoin='CoursePrerequisite.PrerequisiteCourseID == CourseOverview.CourseID', backref='CoursePrerequisite')

    #courseoverview = db.relationship(CourseOverview, backref='courseprerequisite')

    def json(self):
        return {'MainCourseID': self.MainCourseID, 'PrerequisiteCourseID':self.PrerequisiteCourseID }


class SectionOverview(db.Model):
    __tableName__ = 'SectionOverview'
    __mapper_args__ = {'polymorphic_identity': 'SectionOverview'}
    SectionID = db.Column(db.Integer, primary_key=True)
    CourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False, primary_key=True)
    SectionDescription = db.Column(db.String(10000), nullable=False)
    SectionProgress = db.Column(db.Float(precision=2),nullable=False)

    def __init__(self, SectionID, CourseID,SectionDescription,SectionProgress):
        self.SectionID = SectionID
        self.CourseID = CourseID
        self.SectionDescription = SectionDescription
        self.SectionProgress = SectionProgress

    #SectionOverview = db.relationship('SectionOverview', primaryjoin='sectionoverview.CourseID == courseoverview.CourseID', backref='courseoverview')
    CourseOverview = db.relationship('CourseOverview', primaryjoin='SectionOverview.CourseID == CourseOverview.CourseID', backref='SectionOverview')

    def json(self):
        return {'SectionID': self.SectionID, 'CourseID':self.CourseID , 'SectionDescription':self.SectionDescription ,'SectionProgress':self.SectionProgress }

class SectionMaterials(db.Model):
    __tableName__ = 'SectionMaterials'
    __mapper_args__ = {'polymorphic_identity': 'SectionMaterials'}
    SectionMaterialsID = db.Column(db.Integer, primary_key=True)
    SectionID = db.Column(db.ForeignKey(SectionOverview.SectionID), nullable=False, primary_key=True)
    SectionMaterials = db.Column(db.String(10000), nullable=False)
    CourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False, primary_key=True)
    # SectionDescription = db.Column(db.String(100), nullable=False)
    # SectionProgress = db.Column(db.Float(precision=2),nullable=False)

    def __init__(self, SectionMaterialsID, SectionID,SectionMaterials,CourseID):
        self.SectionMaterialsID = SectionMaterialsID
        self.SectionID = SectionID
        self.SectionMaterials = SectionMaterials
        self.CourseID = CourseID

    #SectionMaterials = db.relationship('SectionMaterials', primaryjoin='sectionmaterial.SectionID == sectionoverview.SectionID', backref='sectionoverview')
    #SectionMaterials = db.relationship('SectionMaterials', primaryjoin='sectionmaterial.CourseID == courseoverview.CourseID', backref='courseoverview')

    SectionOverview = db.relationship('SectionOverview', primaryjoin='SectionMaterials.SectionID == SectionOverview.SectionID', backref='SectionMaterials')
    CourseOverview = db.relationship('CourseOverview', primaryjoin='SectionMaterials.CourseID == CourseOverview.CourseID', backref='SectionMaterials')

    def json(self):
        return {'SectionMaterialsID': self.SectionMaterialsID, 'SectionID':self.SectionID , 'SectionMaterials':self.SectionMaterials ,'CourseID':self.CourseID }


class SectionQuiz(db.Model):
    __tableName__ = 'SectionQuiz'
    __mapper_args__ = {'polymorphic_identity': 'SectionQuiz'}
    SectionQuizID = db.Column(db.Integer, primary_key=True)
    SectionID = db.Column(db.ForeignKey(SectionOverview.SectionID), nullable=False, primary_key=True)
    CourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False, primary_key=True)
    SectionMaterialsID = db.Column(db.Integer, primary_key=True)
    quizResult = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Integer, primary_key=True)
    quizStartTime = db.Column(db.String(100), nullable=False)

    #SectionMaterials = db.relationship('SectionQuiz', primaryjoin='sectionquiz.SectionMaterialsID == sectionmaterials.SectionMaterialsID', backref='sectionmaterials')
    #SectionMaterials = db.relationship('SectionQuiz', primaryjoin='sectionquiz.SectionID == sectionoverview.SectionID', backref='sectionoverview')
    #SectionMaterials = db.relationship('SectionQuiz', primaryjoin='sectionquiz.CourseID == courseoverview.CourseID', backref='courseoverview')

    SectionOverview = db.relationship('SectionOverview', primaryjoin='SectionQuiz.SectionID == SectionOverview.SectionID', backref='SectionQuiz')
    CourseOverview = db.relationship('CourseOverview', primaryjoin='SectionQuiz.CourseID == CourseOverview.CourseID', backref='SectionQuiz')

    def __init__(self, SectionQuizID, SectionID, CourseID, SectionMaterialsID,quizResult,duration,quizStartTime):
        self.SectionQuizID = SectionQuizID
        self.SectionID = SectionID
        self.CourseID = CourseID
        self.SectionMaterialsID = SectionMaterialsID
        self.quizResult = quizResult
        self.duration = duration
        self.quizStartTime = quizStartTime
    def json(self):
        return {'SectionQuizID': self.SectionQuizID, 'SectionID':self.SectionID , 'CourseID':self.CourseID ,'SectionMaterialsID':self.SectionMaterialsID ,'quizResult':self.quizResult ,'duration':self.duration ,'quizStartTime':self.quizStartTime }


class TrainerSchedule(db.Model):
    __tableName__ = 'TrainerSchedule'
    __mapper_args__ = {'polymorphic_identity': 'TrainerSchedule'}
    TrainerID = db.Column(db.ForeignKey(Trainer.TrainerID), nullable=False, primary_key=False)
    CourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False)
    TrainerScheduleID = db.Column(db.Integer,nullable=False, primary_key=True)

    #TrainerSchedule = db.relationship('TrainerSchedule', primaryjoin='trainerschedule.TrainerID == trainer.TrainerID', backref='trainer')
    #TrainerSchedule = db.relationship('TrainerSchedule', primaryjoin='trainerschedule.CourseID == courseoverview.CourseID', backref='courseoverview')
    
    def __init__(self, TrainerID, CourseID,TrainerScheduleID):
        self.TrainerID = TrainerID
        self.CourseID = CourseID
        self.TrainerScheduleID = TrainerScheduleID

    Trainer = db.relationship('Trainer', primaryjoin='TrainerSchedule.TrainerID == Trainer.TrainerID', backref='TrainerSchedule')
    CourseOverview = db.relationship('CourseOverview', primaryjoin='TrainerSchedule.CourseID == CourseOverview.CourseID', backref='TrainerSchedule')


    def json(self):
        return {'TrainerID': self.TrainerID, 'CourseID':self.CourseID , 'TrainerScheduleID':self.TrainerScheduleID}


class ClassDescription(db.Model):
    __tableName__ = 'ClassDescription'
    __mapper_args__ = {'polymorphic_identity': 'ClassDescription'}
    CourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False, primary_key=True)
    ClassID = db.Column(db.Integer,nullable=False, primary_key=True)
    ClassSize = db.Column(db.Integer, nullable=False)
    StartTime = db.Column(db.String(100), nullable=False)
    StartDate = db.Column(db.String(100), nullable=False)
    EndTime = db.Column(db.String(100), nullable=False)
    EndDate = db.Column(db.String(100), nullable=False)

    def __init__(self, CourseID, ClassID,ClassSize,StartTime,StartDate,EndTime,EndDate):
        self.CourseID = CourseID
        self.ClassID = ClassID
        self.ClassSize = ClassSize
        self.StartTime = StartTime
        self.StartDate = StartDate
        self.EndTime = EndTime
        self.EndDate = EndDate

    #ClassDescription = db.relationship('ClassDescription', primaryjoin='classdescription.CourseID == courseoverview.CourseID', backref='courseoverview')
    CourseOverview = db.relationship('CourseOverview', primaryjoin='ClassDescription.CourseID == CourseOverview.CourseID', backref='ClassDescription')

   
    def json(self):
        return {'CourseID': self.CourseID, 'ClassID':self.ClassID , 'ClassSize':self.ClassSize, 
                'StartTime':self.StartTime,'StartDate':self.StartDate,'EndTime':self.EndTime,'EndDate':self.EndDate}

class CourseRecord(db.Model):
    __tableName__ = 'CourseRecord'
    __mapper_args__ = {'polymorphic_identity': 'CourseRecord'}
    CourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False)
    #added Courserecord ID here
    CourseRecordID = db.Column(db.Integer,nullable=False, primary_key=True)
    TrainerScheduleID = db.Column(db.ForeignKey(TrainerSchedule.TrainerScheduleID), nullable=False, primary_key=True)
    LearnerID = db.Column(db.ForeignKey(Learner.LearnerID), nullable=False, primary_key=True)
    ClassID = db.Column(db.ForeignKey(ClassDescription.ClassID), nullable=False, primary_key=True)
    CourseProgress = db.Column(db.Float)
    FinalQuizResult = db.Column(db.String(100))

    def __init__(self, CourseID, CourseRecordID,TrainerScheduleID,LearnerID,ClassID,CourseProgress,FinalQuizResult):
        self.CourseID = CourseID
        self.CourseRecordID = CourseRecordID
        self.TrainerScheduleID = TrainerScheduleID
        self.LearnerID = LearnerID
        self.ClassID = ClassID
        self.CourseProgress = CourseProgress
        self.FinalQuizResult = FinalQuizResult
    #Here got issue => Need to use CourseRecord then join into TrainerSchedule table to Trainer & Trainschedule to courseoverview in 1 line
    #CourseRecord = db.relationship('trainer', primaryjoin='trainerschedule.TrainerID == trainer.TrainerID', backref='TrainerSchedule')
    #CourseRecord = db.relationship('courseoverview', primaryjoin='trainerschedule.CourseID == courseoverview.CourseID', backref='TrainerSchedule')

    CourseOverview = db.relationship('CourseOverview', primaryjoin='CourseRecord.CourseID == CourseOverview.CourseID', backref='CourseRecord')
    TrainerSchedule = db.relationship('TrainerSchedule', primaryjoin='CourseRecord.TrainerScheduleID == TrainerSchedule.TrainerScheduleID', backref='CourseRecord')
    Learner = db.relationship('Learner', primaryjoin='CourseRecord.LearnerID == Learner.LearnerID', backref='CourseRecord')
    ClassDescription = db.relationship('ClassDescription', primaryjoin='CourseRecord.ClassID == ClassDescription.ClassID', backref='CourseRecord')

    def json(self):
        return {'CourseID': self.CourseID, 'CourseRecordID': self.CourseRecordID, 'TrainerScheduleID':self.TrainerScheduleID , 'LearnerID':self.LearnerID, 
        'ClassID':self.ClassID,'CourseProgress':self.CourseProgress,'FinalQuizResult':self.FinalQuizResult }



class Enrollment(db.Model):
    __tableName__ = 'Enrollment'
    __mapper_args__ = {'polymorphic_identity': 'Enrollment'}
    LearnerID = db.Column(db.ForeignKey(Learner.LearnerID), nullable=False)
    EnrollmentID = db.Column(db.Integer,nullable=False, primary_key=True)
    CourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False)
    ClassID = db.Column(db.ForeignKey(ClassDescription.ClassID), nullable=False)
    Approved = db.Column(db.Boolean, nullable=False)
    passPrerequisite = db.Column(db.Boolean, nullable=False)

    #Enrollment = db.relationship('Enrollment', primaryjoin='enrollment.LearnerID == learner.LearnerID', backref='learner')
    #Enrollment = db.relationship('Enrollment', primaryjoin='enrollment.CourseID == courseoverview.CourseID', backref='courseoverview')
    #Enrollment = db.relationship('Enrollment', primaryjoin='enrollment.ClassID == classdescription.ClassID', backref='classdescription')
    
    def __init__(self, LearnerID, EnrollmentID,CourseID,ClassID,Approved,passPrerequisite):
        self.LearnerID = LearnerID
        self.EnrollmentID = EnrollmentID
        self.CourseID = CourseID
        self.LearnerID = LearnerID
        self.ClassID = ClassID
        self.Approved = Approved
        self.passPrerequisite = passPrerequisite

    CourseOverview = db.relationship('CourseOverview', primaryjoin='Enrollment.CourseID == CourseOverview.CourseID', backref='Enrollment')
    Learner = db.relationship('Learner', primaryjoin='Enrollment.LearnerID == Learner.LearnerID', backref='Enrollment')
    ClassDescription = db.relationship('ClassDescription', primaryjoin='Enrollment.ClassID == ClassDescription.ClassID', backref='Enrollment')


    def json(self):
        return {'LearnerID': self.LearnerID, 'EnrollmentID': self.EnrollmentID, 'CourseID': self.CourseID, 'ClassID': self.ClassID,
        'Approved' :self.Approved, 'passPrerequisite': self.passPrerequisite}



#Here probably have the same issue as the codes above
class QuizQn(db.Model):
    __tableName__ = 'QuizQn'
    __mapper_args__ = {'polymorphic_identity': 'QuizQn'}
    QuizQnID = db.Column(db.Integer,nullable=False, primary_key=True)
    CourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False)
    SectionMaterialsID = db.Column(db.ForeignKey(SectionMaterials.SectionMaterialsID), nullable=False, primary_key=True)
    SectionQuizID = db.Column(db.ForeignKey(SectionQuiz.SectionQuizID), nullable=False, primary_key=True)
    SectionID = db.Column(db.ForeignKey(SectionOverview.SectionID), nullable=False, primary_key=True)
    QuizQuestion = db.Column(db.String(10000), nullable=False)
    QuizOptionNo = db.Column(db.Integer, nullable=False, primary_key=True)
    QuizOption = db.Column(db.String(10000), nullable=False)

    #QuizQn = db.relationship('QuizQn', primaryjoin='QuizQn.CourseID == courseoverview.CourseID', backref='courseoverview')
    #QuizQn = db.relationship('QuizQn', primaryjoin='QuizQn.SectionMaterialsID == sectionoverview.SectionMaterialsID', backref='sectionoverview')
    #QuizQn = db.relationship('QuizQn', primaryjoin='QuizQn.SectionQuizID == sectionoverview.SectionQuizID', backref='sectionoverview')
    #QuizQn = db.relationship('QuizQn', primaryjoin='QuizQn.SectionID == sectionoverview.SectionID', backref='sectionoverview')
    
    def __init__(self, QuizQnID, CourseID,SectionMaterialsID,SectionQuizID,SectionID,QuizQuestion,QuizOptionNo,QuizOption):
        self.QuizQnID = QuizQnID
        self.CourseID = CourseID
        self.SectionMaterialsID = SectionMaterialsID
        self.SectionQuizID = SectionQuizID
        self.SectionID = SectionID
        self.QuizQuestion = QuizQuestion
        self.QuizOptionNo = QuizOptionNo
        self.QuizOption = QuizOption


    CourseOverview = db.relationship('CourseOverview', primaryjoin='QuizQn.CourseID == CourseOverview.CourseID', backref='QuizQn')
    SectionMaterials = db.relationship('SectionMaterials', primaryjoin='QuizQn.SectionMaterialsID == SectionMaterials.SectionMaterialsID', backref='QuizQn')
    SectionQuiz = db.relationship('SectionQuiz', primaryjoin='QuizQn.SectionQuizID == SectionQuiz.SectionQuizID', backref='QuizQn')
    SectionOverview = db.relationship('SectionOverview', primaryjoin='QuizQn.SectionID == SectionOverview.SectionID', backref='QuizQn')

    def json(self):
        return {'QuizQnID': self.QuizQnID,'CourseID': self.CourseID, 'SectionMaterialsID':self.SectionMaterialsID, 'SectionQuizID':self.SectionQuizID, 'SectionID':self.SectionID, 'QuizQuestion': self.QuizQuestion, 'QuizOptionNo': self.QuizOptionNo, 'QuizOption': self.QuizOption }

class LearnerQuizAnswer(db.Model):
    __tableName__ = 'LearnerQuizAnswer'
    __mapper_args__ = {'polymorphic_identity': 'LearnerQuizAnswer'}
    QuizQnID = db.Column(db.ForeignKey(QuizQn.QuizQnID),nullable=False, primary_key=True)
    SectionQuizID = db.Column(db.ForeignKey(SectionQuiz.SectionQuizID), nullable=False, primary_key=True)
    SectionMaterialsID = db.Column(db.ForeignKey(SectionMaterials.SectionMaterialsID), nullable=False, primary_key=True)
    CourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False, primary_key=True)
    SectionID = db.Column(db.ForeignKey(SectionOverview.SectionID), nullable=False, primary_key=True)
    LearnerID = db.Column(db.ForeignKey(Learner.LearnerID), nullable=False, primary_key=True)
    quizAnswer = db.Column(db.String(10000), nullable=False)

    #LearnerQuizAnswer = db.relationship('LearnerQuizAnswer', primaryjoin='learnerquizanswer.CourseID == courseoverview.CourseID', backref='courseoverview')
    #LearnerQuizAnswer = db.relationship('LearnerQuizAnswer', primaryjoin='learnerquizanswer.QuizQnID == sectionoverview.QuizQnID', backref='sectionoverview')
    #LearnerQuizAnswer = db.relationship('LearnerQuizAnswer', primaryjoin='learnerquizanswer.SectionQuizID == sectionoverview.SectionQuizID', backref='sectionoverview')
    #LearnerQuizAnswer = db.relationship('LearnerQuizAnswer', primaryjoin='learnerquizanswer.SectionID == sectionoverview.SectionID', backref='sectionoverview')
    #LearnerQuizAnswer = db.relationship('LearnerQuizAnswer', primaryjoin='learnerquizanswer.LearnerID == learner.LearnerID', backref='learner')
    #LearnerQuizAnswer = db.relationship('LearnerQuizAnswer', primaryjoin='learnerquizanswer.SectionMaterialsID == sectionoverview.SectionMaterialsID', backref='sectionoverview')
    
    def __init__(self, QuizQnID, SectionQuizID,SectionMaterialsID,CourseID,SectionID,LearnerID,quizAnswer):
        self.QuizQnID = QuizQnID
        self.SectionQuizID = SectionQuizID
        self.SectionMaterialsID = SectionMaterialsID
        self.CourseID = CourseID
        self.SectionID = SectionID
        self.LearnerID = LearnerID
        self.quizAnswer = quizAnswer

    QuizQn = db.relationship('QuizQn', primaryjoin='LearnerQuizAnswer.QuizQnID == QuizQn.QuizQnID', backref='LearnerQuizAnswer')
    CourseOverview = db.relationship('CourseOverview', primaryjoin='LearnerQuizAnswer.CourseID == CourseOverview.CourseID', backref='LearnerQuizAnswer')
    SectionMaterials = db.relationship('SectionMaterials', primaryjoin='LearnerQuizAnswer.SectionMaterialsID == SectionMaterials.SectionMaterialsID', backref='LearnerQuizAnswer')
    SectionQuiz = db.relationship('SectionQuiz', primaryjoin='LearnerQuizAnswer.SectionQuizID == SectionQuiz.SectionQuizID', backref='LearnerQuizAnswer')
    SectionOverview = db.relationship('SectionOverview', primaryjoin='LearnerQuizAnswer.SectionID == SectionOverview.SectionID', backref='LearnerQuizAnswer')
    Learner = db.relationship('Learner', primaryjoin='LearnerQuizAnswer.LearnerID == Learner.LearnerID', backref='LearnerQuizAnswer')

    def json(self):
        return {'QuizQnID': self.QuizQnID, 'SectionQuizID':self.SectionQuizID, 'SectionMaterialsID':self.SectionMaterialsID, 'CourseID':self.CourseID
                , 'SectionID':self.SectionID, 'LearnerID':self.LearnerID, 'quizAnswer':self.quizAnswer}


    
class SolutionTable(db.Model):
    __tableName__ = 'SolutionTable'
    __mapper_args__ = {'polymorphic_identity': 'LearnerQuizAnswer'}
    QuizQnID = db.Column(db.ForeignKey(QuizQn.QuizQnID),nullable=False, primary_key=True)
    SectionQuizID = db.Column(db.ForeignKey(SectionQuiz.SectionQuizID), nullable=False, primary_key=True)
    SectionMaterialsID = db.Column(db.ForeignKey(SectionMaterials.SectionMaterialsID), nullable=False, primary_key=True)
    CourseID = db.Column(db.ForeignKey(CourseOverview.CourseID), nullable=False, primary_key=True)
    SectionID = db.Column(db.ForeignKey(SectionOverview.SectionID), nullable=False, primary_key=True)
    quizSolution = db.Column(db.String(10000), nullable=False)

    #SolutionTable = db.relationship('SolutionTable', primaryjoin='solutiontable.CourseID == courseoverview.CourseID', backref='courseoverview')
    #SolutionTable = db.relationship('SolutionTable', primaryjoin='solutiontable.QuizQnID == sectionoverview.QuizQnID', backref='sectionoverview')
    #SolutionTable = db.relationship('SolutionTable', primaryjoin='solutiontable.SectionQuizID == sectionoverview.SectionQuizID', backref='sectionoverview')
    #SolutionTable = db.relationship('SolutionTable', primaryjoin='solutiontable.SectionID == sectionoverview.SectionID', backref='sectionoverview')
    #SolutionTable = db.relationship('SolutionTable', primaryjoin='solutiontable.SectionMaterialsID == sectionoverview.SectionMaterialsID', backref='sectionoverview')

    def __init__(self, QuizQnID, SectionQuizID,SectionMaterialsID,CourseID,SectionID,quizSolution):
        self.QuizQnID = QuizQnID
        self.SectionQuizID = SectionQuizID
        self.SectionMaterialsID = SectionMaterialsID
        self.CourseID = CourseID
        self.SectionID = SectionID
        self.quizSolution = quizSolution

    QuizQn = db.relationship('QuizQn', primaryjoin='SolutionTable.QuizQnID == QuizQn.QuizQnID', backref='SolutionTable')
    CourseOverview = db.relationship('CourseOverview', primaryjoin='SolutionTable.CourseID == CourseOverview.CourseID', backref='SolutionTable')
    SectionMaterials = db.relationship('SectionMaterials', primaryjoin='SolutionTable.SectionMaterialsID == SectionMaterials.SectionMaterialsID', backref='SolutionTable')
    SectionQuiz = db.relationship('SectionQuiz', primaryjoin='SolutionTable.SectionQuizID == SectionQuiz.SectionQuizID', backref='SolutionTable')
    SectionOverview = db.relationship('SectionOverview', primaryjoin='SolutionTable.SectionID == SectionOverview.SectionID', backref='SolutionTable')


    def json(self):
        return {'QuizQnID': self.QuizQnID, 'SectionQuizID':self.SectionQuizID, 'SectionMaterialsID':self.SectionMaterialsID, 'CourseID':self.CourseID
                , 'SectionID':self.SectionID, 'quizSolution':self.quizSolution}


    
@app.route('/person') 
def trainer_by_email(): 
    trainerDetails = Person.query.all() 
    if trainerDetails: 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "Trainer": "works" 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "Trainer Details not found." 
        } 
    ), 404 

@app.route('/person/<int:PersonID>') 
def person_by_id(PersonID): 
    PersonDetails = Person.query.filter_by(PersonID=PersonID).all() 
    if PersonDetails: 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "Person":  [persons.json() for persons in PersonDetails]  
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "Trainer Details not found." 
        } 
    ), 404 
 

@app.route('/learner/<int:LearnerID>') 
def learner_by_id(LearnerID): 
    learnerDetails = Learner.query.filter_by(LearnerID=LearnerID).all() 
    if learnerDetails: 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "Learner":  [learners.json() for learners in learnerDetails]  
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "Learner Details not found." 
        } 
    ), 404 
 
@app.route('/enrollment', methods=['GET']) 
def enrollment(): 
    enrollmentRecords = Enrollment.query.all() 
    if len(enrollmentRecords): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "Enrollment":  [courses.json() for courses in enrollmentRecords]  
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "Enrollment details not found." 
        } 
    ), 404 


@app.route('/enrolledAllPerson', methods=['GET']) 
def getAllPerson(): 
    enrollmentRecords = Person.query.all() 
    if len(enrollmentRecords): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "Enrollment":  [courses.json() for courses in enrollmentRecords]  
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "Enrollment details not found." 
        } 
    ), 404 


@app.route('/courserecord', methods=['GET']) 
def courserecord(): 
    courseRecords = CourseRecord.query.all() 
    if len(courseRecords): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "CourseRecords":  [courses.json() for courses in courseRecords]  
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "Enrollment details not found." 
        } 
    ), 4

@app.route('/courserecord/<int:CourseID>', methods=['GET']) 
def getCourserecordbyID(CourseID): 
    courseRecords = CourseRecord.query.filter_by(CourseID=CourseID).all() 
    if len(courseRecords): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "CourseRecords":  [courses.json() for courses in courseRecords]  
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No course records with given ID" 
        } 
    ), 4


@app.route('/getCourseName/<int:CourseID>', methods=['GET']) 
def getCourseName(CourseID): 
    courseRecords = CourseOverview.query.filter_by(CourseID=CourseID).all() 
    if len(courseRecords): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "CourseOverview":  [courses.json() for courses in courseRecords]  
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "Enrollment details not found." 
        } 
    ), 4

@app.route('/getEnrollment/<int:EnrollmentID>', methods=['GET']) 
def getEnrollment(EnrollmentID): 
    enrollmentRecords = Enrollment.query.filter_by(EnrollmentID=EnrollmentID).all() 
    if len(enrollmentRecords): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "Enrollment":  [courses.json() for courses in enrollmentRecords]  
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "Enrollment details not found." 
        } 
    ), 404 

@app.route('/trainerSchedule/<int:CourseID>', methods=['GET']) 
def trainerSchedule(CourseID): 
    trainerRecords = TrainerSchedule.query.filter_by(CourseID=CourseID).all() 
    if len(trainerRecords): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "Enrollment":  [courses.json() for courses in trainerRecords]  
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "Trainer schedule details not found." 
        } 
    ), 404 

@app.route('/insertCourseRecord', methods=['GET','POST']) 
def insertCourseRecord(): 
    CourseID = request.get_json()["CourseID"]
    TrainerScheduleID = request.get_json()["TrainerScheduleID"]
    LearnerID = request.get_json()["LearnerID"]
    ClassID= request.get_json()["ClassID"]
    CourseProgress = request.get_json()["CourseProgress"]
    FinalQuizResult = request.get_json()["FinalQuizResult"]
    
    # if (CourseRecord.query.filter_by(CourseID=CourseID, TrainerScheduleID=TrainerScheduleID,LearnerID=LearnerID).first()):
    #     return jsonify(
    #         {
    #             "code": 400,
    #             "message": "CourseRecord already created."
    #         }
    #     ), 400
    # else :
    #Courserecord = CourseRecord()
    Courserecord = CourseRecord(CourseRecordID=None, CourseID=CourseID,TrainerScheduleID=TrainerScheduleID,LearnerID=LearnerID,ClassID=ClassID,CourseProgress=CourseProgress,FinalQuizResult=FinalQuizResult)
 
    try:
        db.session.add(Courserecord)
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "message": "Insertion Successful"
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the quiz. "
            }
        ), 500

 
@app.route('/class') 
def classes(): 
    courseList = ClassDescription.query.all() 
    if len(courseList): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                   "courses": [courses.json() for courses in courseList] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "Enrollment details not found." 
        } 
    ), 404 
 
 
# @app.route("/retrievecompletedcourse/<int:LearnerID>") 
# def retrievecompletedcourse(LearnerID): 
#     #I have to join with Trainer table & class table => because of primary key => FK constraints
#     rows = db.session.query(CourseRecord).filter((Learner.LearnerID == CourseRecord.LearnerID) & (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & ((CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded'))).all()
#     #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
#     if len(rows): 
#         return jsonify( 
#             { 
#                 "code": 200, 
#                 "data": { 
#                     "courses": [courses.json() for courses in rows] 
#                 } 
#             } 
#         ) 
#     return jsonify( 
#         { 
#             "code": 404, 
#             "message": "No enrollment available for selected student." 
#         } 
#     ), 404
 
@app.route("/retrieveCourseNameCompleted/<int:LearnerID>") 
def retrieveCourseNameCompleted(LearnerID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(CourseOverview).filter((CourseOverview.CourseID == CourseRecord.CourseID) & (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & ((CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded'))).all()
    #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404
 
@app.route("/courseoverview") 
def retrieveCourseName(): 
    CourseList = CourseOverview.query.all() 
    if len(CourseList): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in CourseList] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404 

@app.route("/courseoverview/<int:CourseID>") 
def retrieveCourseOverview(CourseID): 
    CourseList = CourseOverview.query.filter_by(CourseID=CourseID).all() 
    if len(CourseList): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in CourseList] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404


@app.route("/learnerDetails/<int:LearnerID>") 
def retrievelearnerDetails(LearnerID): 
    data = db.session.query(Person, Learner)\
    .filter(
    (Learner.LearnerID == LearnerID)
    & (Learner.PersonID==Person.PersonID)
    & (Person.PersonID==Learner.PersonID)
    ).first()

    if (data): 
        return jsonify({
            "code": 200, 
            "data": {
                **data.Person.json()
            }
                }
            )

@app.route("/updateEnrollment/<int:enrollmentID>") 
def updateEnrollment(enrollmentID):
    try: 
        enroll = Enrollment.query.filter_by(EnrollmentID=enrollmentID).first()
        enroll.Approved = True
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "data": {
                    "EnrollmentID": enrollmentID
                },
                "message": "Update Successful"
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "EnrollmentID": enrollmentID
                },
                "message": "An error occurred while updating the payment. " + str(e)
            }
        ), 500

@app.route("/getCourseRecords", methods=['GET','POST']) 
def getCourseRecords():
    data = request.get_json()
    #print(data)
    LearnerIDs =  data['ID']
    LearnerList= db.session.query(Learner).filter(Learner.LearnerID.notin_(LearnerIDs)) 
    if (LearnerList): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "Learners": [learners.json() for learners in LearnerList] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404 

@app.route("/removeCourseRecords", methods=['GET','POST']) 
def removeCourseRecords():
    data = request.get_json()
    #print(data)
    courseRecordID =  data['ID']
    try: 
        # deleted_objects = CourseRecord.__table__.delete().where(CourseRecord.CourseID.in_(courseRecordID))
        # db.session.execute(deleted_objects)
        # db.session.commit()

        sql1 = delete(CourseRecord).where(CourseRecord.CourseRecordID.in_(courseRecordID))

        db.session.execute(sql1)
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "data": {
                    "courseRecordIDs": courseRecordID
                },
                "message": "Deletion Successful"
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "courseRecordIDs": courseRecordID
                },
                "message": "An error occurred while deleting the course records. " + str(e)
            }
        ), 500


@app.route("/sectionoverview") 
def retrieveSectionOverview(): 
    SectionList = SectionOverview.query.all() 
    if len(SectionList): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [sections.json() for sections in SectionList] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404 

@app.route("/sectionmaterials") 
def retrieveSectionMaterials(): 
    SectionList = SectionMaterials.query.all() 
    if len(SectionList): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [sections.json() for sections in SectionList] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No section materials available for selected student." 
        } 
    ), 404 

@app.route("/sectionquiz") 
def retrieveSectionQuiz(): 
    SectionQuizList = SectionQuiz.query.all()
    if len(SectionQuizList): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "sectionquiz": [sectionquiz.json() for sectionquiz in SectionQuizList] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No sectionquiz available." 
        } 
    ), 404 


@app.route("/retrieveCourseProgress/<int:LearnerID>") 
def retrieveCourseProgress(LearnerID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(CourseRecord).join(CourseOverview).filter(CourseRecord.LearnerID == LearnerID).all()
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404

@app.route("/individualcourse/<int:LearnerID>") 
def retrieveCourseNameID(LearnerID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(CourseOverview).join(CourseRecord).filter(CourseRecord.LearnerID == LearnerID).all()
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404
    #SELECT a.*, b.* from course_record a, course_prerequisite b where a.CourseID = b.PrerequisiteCourseID and a.LearnerID = 1
#and a.CourseProgress = 100 and (a.FinalQuizResult ='Pass' or a.FinalQuizResult = 'Ungraded')

@app.route("/sectionquiz/<string:SectionQuizID>")
def find_by_SectionQuizID(SectionQuizID):
    sectionquiz = SectionQuiz.query.filter_by(SectionQuizID=SectionQuizID).first()
    if sectionquiz:
        return jsonify(
            {
                "code": 200,
                "data": sectionquiz.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Sectionquiz not found."
        }
    ), 404


@app.route("/createsectionquiz", methods=['GET','POST'])
def create_sectionquiz():
    SectionID = request.get_json()["SectionID"]
    SectionMaterialsID = request.get_json()["SectionMaterialsID"]
    CourseID = request.get_json()["CourseID"]
    quizResult = request.get_json()["quizResult"]
    duration = request.get_json()["duration"]
    quizStartTime = request.get_json()["quizStartTime"]

    Sectionquiz = SectionQuiz(SectionQuizID=None, SectionID=SectionID,SectionMaterialsID=SectionMaterialsID,CourseID=CourseID,quizResult=quizResult, duration=duration, quizStartTime=quizStartTime)
 
    try:
        db.session.add(Sectionquiz)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Creation of quiz success. "
            }
        ), 500
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the quiz. "
            }
        ), 500

@app.route("/quizquestions") 
def retrieveQuizQn(): 
    QuizQnList = QuizQn.query.all()
    if len(QuizQnList): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "quizquestions": [quizquestions.json() for quizquestions in QuizQnList] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No sectionquiz available." 
        } 
    ), 404 

@app.route("/quizquestions/<int:QuizQnID>")
def find_by_QuizQuestions(QuizQnID):
    quizquestions = QuizQn.query.filter_by(QuizQnID=QuizQnID).all()
    if quizquestions:
        return jsonify(
            {
                "code": 200,
                "data": [quizquestions.json() for quizquestions in quizquestions] 
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "quizquestions not found."
        }
    ), 404

@app.route("/quizquestionsNo/<int:SectionQuizID>")
def getNumOfQuestions(SectionQuizID):
    sql = db.session.query(QuizQn.QuizQnID.distinct()).filter_by(SectionQuizID = SectionQuizID).count()
    if sql:
        return jsonify(
            {
                "code": 200,
                "data": sql
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "quizquestions not found."
        }
    ), 404


@app.route("/solutiontable") 
def retrieveSolutionTable(): 
    SolutionTableList = SolutionTable.query.all()
    if len(SolutionTableList): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "solutions": [solutions.json() for solutions in SolutionTableList] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No sectionquiz available." 
        } 
    ), 404 

@app.route("/learnerquizanswer") 
def publishlearneranswer(): 
    SectionQuizList = SectionQuiz.query.all()
    if len(SectionQuizList): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "sectionquiz": [sectionquiz.json() for sectionquiz in SectionQuizList] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No sectionquiz available." 
        } 
    ), 404 

@app.route("/learnerquizanswer", methods=['POST'])
def publish_learnerquizanswer():
    QuizQnID = request.get_json()["QuizQnID"]
    SectionQuizID = request.get_json()["SectionQuizID"]
    SectionMaterialsID = request.get_json()["SectionMaterialsID"]
    CourseID = request.get_json()["CourseID"]
    SectionID = request.get_json()["SectionID"]
    LearnerID = request.get_json()["LearnerID"]
    quizAnswer = request.get_json()["quizAnswer"]

    learnerquiz = LearnerQuizAnswer(QuizQnID=QuizQnID,SectionQuizID=SectionQuizID, SectionMaterialsID=SectionMaterialsID,CourseID=CourseID,SectionID=SectionID,LearnerID=LearnerID, quizAnswer=quizAnswer)
 
    try:
        db.session.add(learnerquiz)
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "message": "Learner quiz answer successful"
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while learner submit the answers for quiz. "
            }
        ), 500

@app.route("/retrieveinprogress/<int:CourseID>") 
def retrieveCourseNameByCoursesID(CourseID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = CourseOverview.query.filter_by(CourseID=CourseID).all() 
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404

@app.route("/trainerschedule/<int:CourseID>") 
def retrieveTrainerSchedule(CourseID): 
    schedule = TrainerSchedule.query.filter_by(CourseID=CourseID).all() 
    if len(schedule): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "trainerschedules": [x.json() for x in schedule] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No schedule available for selected course." 
        } 
    ), 404

@app.route("/trainer/<int:TrainerID>") 
def retrieveTrainer(TrainerID): 
    trainer = Trainer.query.filter_by(TrainerID=TrainerID).all() 
    if len(trainer): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "trainers": [x.json() for x in trainer] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No trainer available for selected trainer ID." 
        } 
    ), 404

@app.route("/prerequisite/<int:CourseID>") 
def retrievePrerequisite(CourseID): 
    prerequisite = CoursePrerequisite.query.filter_by(MainCourseID=CourseID).all() 
    if len(prerequisite): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "trainers": [x.json() for x in prerequisite] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No prerequisite available for selected course ID." 
        } 
    ), 404

@app.route('/insertSelfEnrol', methods=['POST']) 
def insertSelfEnrol(): 
    LearnerID = request.get_json()["LearnerID"]
    CourseID = request.get_json()["CourseID"]
    ClassID = request.get_json()["ClassID"]
    Approved= request.get_json()["Approved"]
    passPrerequisite = request.get_json()["passPrerequisite"]

    selfEnrol = Enrollment(LearnerID=LearnerID, EnrollmentID=None, CourseID=CourseID,ClassID=ClassID,Approved=Approved,passPrerequisite=passPrerequisite)
 
    try:
        db.session.add(selfEnrol)
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "message": "Insertion Successful"
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the enrolment. "
            }
        ), 500
@app.route("/retrieveCoursesID/<int:CourseID>") 
def retrieveSpecificCourseByID(CourseID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(CourseOverview).filter((SectionOverview.CourseID == CourseRecord.CourseID) & (CourseOverview.CourseID == CourseID)).all()
    #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404   

@app.route("/retrieveSectionsByID/<int:CourseID>") 
def retrieveSections(CourseID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(SectionOverview).filter((SectionOverview.CourseID == SectionMaterials.CourseID) & (SectionOverview.SectionID == SectionMaterials.SectionID) & (SectionOverview.CourseID == CourseID)).all()
    #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404   


@app.route("/retrieveSectionMaterialsByCourseID/<int:CourseID>") 
def retrieveSectionMaterialsByCourseID(CourseID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(SectionQuiz).filter((SectionOverview.CourseID == SectionMaterials.CourseID) & (SectionQuiz.CourseID == SectionMaterials.CourseID) & (SectionMaterials.CourseID == CourseID)).all()
    #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404   


@app.route("/sectionmaterialsbyCourse/<int:CourseID>") 
def sectionmaterialsByCourse(CourseID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(SectionMaterials).filter((SectionOverview.CourseID == SectionMaterials.CourseID) & (SectionQuiz.CourseID == SectionMaterials.CourseID) & (SectionMaterials.CourseID == CourseID)).all()
    #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404   

@app.route("/retrievecompletedcourse/<int:LearnerID>") 
def retrievecompletedcourse(LearnerID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(CourseOverview).filter((Learner.LearnerID == CourseRecord.LearnerID) & (CourseRecord.LearnerID == LearnerID) & (CourseOverview.CourseID == CourseRecord.CourseID) & (CourseRecord.CourseProgress == 100) & ((CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded'))).all()
    #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404
 
@app.route("/retrievecompletingcompleted/<int:LearnerID>") 
def retrievecompletingcompleted(LearnerID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(CourseOverview).filter((Learner.LearnerID == CourseRecord.LearnerID) & (CourseRecord.LearnerID == LearnerID) & (CourseOverview.CourseID == CourseRecord.CourseID) & (CourseRecord.CourseProgress  < 100)).all()
    #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404

@app.route("/prereq/<int:LearnerID>") 
def retrievePrereqCourses(LearnerID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID) & (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404

@app.route("/createquizzes", methods=['GET','POST']) 
def Create_Quizzes(): 
 
    QuizQnID = request.get_json()["QuizQnID"] 
    CourseID = request.get_json()["CourseID"] 
    SectionMaterialsID = request.get_json()["SectionMaterialsID"] 
    SectionQuizID = request.get_json()["SectionQuizID"] 
    SectionID = request.get_json()["SectionID"] 
    QuizQuestion = request.get_json()["QuizQuestion"] 
    QuizOptionNo = request.get_json()["QuizOptionNo"] 
    QuizOption = request.get_json()['QuizOption'] 
    Courserecord = QuizQn(QuizQnID=QuizQnID, CourseID=CourseID,SectionMaterialsID=SectionMaterialsID,SectionQuizID=SectionQuizID,SectionID=SectionID,QuizQuestion=QuizQuestion, QuizOptionNo = QuizOptionNo, QuizOption = QuizOption) 
  
    try: 
        db.session.add(Courserecord) 
        db.session.commit() 
    except Exception as e: 
        return jsonify( 
            { 
                "code": 500, 
                "message": "An error occurred while creating the review. " + str(e) 
            } 
        ), 500 
 
    print(json.dumps(Courserecord.json(), default=str)) # convert a JSON object to a string and print 
    print() 
    return jsonify( 
        { 
            "code": 201, 
            "data": Courserecord.json() 
        } 
    ), 201

@app.route("/retrievePrerequisitecourses/<int:LearnerID>") 
def retrieveAllPrereq(LearnerID): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = db.session.query(CoursePrerequisite).filter((CourseRecord.CourseID == CoursePrerequisite.PrerequisiteCourseID) & (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & ((CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded'))).all()
    #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    #I will extract out the CourseID of whatever that the user has already passed then i will for loop it
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404


@app.route("/retrievebooleanfalse") 
def retrieveAllPrereqs(): 
    #I have to join with Trainer table & class table => because of primary key => FK constraints
    rows = CourseOverview.query.filter_by(Prerequisite='FALSE').all() 
    #db.session.query(CoursePrerequisite).join(CourseRecord, CoursePrerequisite).filter((CoursePrerequisite.PrerequisiteCourseID == CourseRecord.CourseID)& (CourseRecord.LearnerID == LearnerID) & (CourseRecord.CourseProgress == 100) & (CourseRecord.FinalQuizResult == 'Pass') |(CourseRecord.FinalQuizResult == 'Ungraded')).all()
    #I will extract out the CourseID of whatever that the user has already passed then i will for loop it
    if len(rows): 
        return jsonify( 
            { 
                "code": 200, 
                "data": { 
                    "courses": [courses.json() for courses in rows] 
                } 
            } 
        ) 
    return jsonify( 
        { 
            "code": 404, 
            "message": "No enrollment available for selected student." 
        } 
    ), 404

   
if __name__ == '__main__': 
    print("This is flask for " + os.path.basename(__file__) + ": retrieve Trainer Details ...") 
    app.run(host='0.0.0.0', port=5016, debug=True)
