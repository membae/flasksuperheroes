from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # Add relationship
    hero_powers = db.relationship("HeroPower", back_populates="hero", cascade='all, delete-orphan')

    # Add serialization rules
    serialize_rules = ('-hero_powers.hero',)

    def to_dict(self):
        hero_dict = {
            "id": self.id,
            "name": self.name,
            "super_name": self.super_name,
           
        }
        return hero_dict

    def __repr__(self):
        return f'<Hero {self.id}, {self.name}, {self.super_name}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship
    hero_powers=db.relationship("HeroPower",back_populates='power',cascade='all, delete-orphan')
    # add serialization rules
    serialize_rules = ('-hero_powers.power',)
    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "description":self.description,
        }
    # add validation
    def validate(self):
        if not self.description:
            raise ValueError("Description must be present.")
        if len(self.description) < 20:
            raise ValueError("Description must be at least 20 characters long.")

    def __repr__(self):
        return f'<Power {self.id},{self.name},{self.description}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # add relationships
    hero_id=db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id=db.Column(db.Integer, db.ForeignKey('powers.id'))

    hero=db.relationship('Hero',back_populates="hero_powers")
    power=db.relationship('Power',back_populates="hero_powers")
    # add serialization rules
    serialize_rules = ('-hero.powers', '-power.heroes')
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
    def validate(self):
        if self.strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be one of the following values: 'Strong', 'Weak', 'Average'.")
    def __repr__(self):
        return f'<HeroPower {self.id},{self.strength},{self.hero.name},{self.power.name}>'
