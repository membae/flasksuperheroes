from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # Add relationship
    hero_powers = db.relationship("HeroPower", back_populates="hero", cascade='all, delete-orphan')

    # Add serialization rules
   

    def to_dict(self):
        hero_dict = {
            "id": self.id,
            "name": self.name,
            "super_name": self.super_name,
           
        }
        return hero_dict

    def __repr__(self):
        return f'<Hero {self.id}, {self.name}, {self.super_name}>'


class Power(db.Model):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship
    hero_powers=db.relationship("HeroPower",back_populates='power',cascade='all, delete-orphan')
    # add serialization rules
    
    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "description":self.description,
        }
    # add validation
    @validates("description")
    def validate(self,key,description):
        if len(description)<20:
            raise ValueError("Description must have at least 20 characters")
        return description


    def __repr__(self):
        return f'<Power {self.id},{self.name},{self.description}>'


class HeroPower(db.Model):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # add relationships
    hero_id=db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id=db.Column(db.Integer, db.ForeignKey('powers.id'))

    hero=db.relationship('Hero',back_populates="hero_powers")
    power=db.relationship('Power',back_populates="hero_powers")
    # add serialization rules
  
    def to_dict(self):
        return {
            "id":self.id,
            "hero_id":self.hero_id,
            "power_id":self.power_id,
            "strength":self.strength,
            "hero": self.hero.to_dict() if self.hero else None,  # Ensure hero exists
            "power": self.power.to_dict() if self.power else None   # Ensure power exists
        }
    # add validation
    @validates("strength")
    def validate(self,key,strength):
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("validation errors")
        return strength
        


    def __repr__(self):
        return f'<HeroPower {self.id},{self.strength},{self.hero.name},{self.power.name}>'
