import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
engine = create_engine('sqlite:///recipes.db')
Base = declarative_base()

# Class declarations

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String(32), index = True)
    password_hash = Column(String(64))

class Cuisine(Base):
    __tablename__ = 'cuisines'
    cuisine_id = Column(String(80), primary_key=True)
    
    @property
    def serialize(self):
        return {
            'cuisine_id' : self.cuisine_id
        }
class Recipe(Base):
    __tablename__ = 'recipes'
    name = Column(String(80), nullable = False)
    description = Column(String(250))
    difficulty = Column(String(80))
    cuisine_id = Column(String, ForeignKey('cuisines.cuisine_id'))
    cuisine = relationship(Cuisine)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)
    id = Column(Integer, primary_key=True)
 
    @property
    def serialize(self):
        return {
            'name' : self.name,
            'description' : self.description,
            'difficulty' : self.difficulty,
            'cuisine_id' : self.cuisine_id,
            'user_id' : self.user_id,
            'id' : self.id
        }

class Ingredient(Base):
    __tablename__ = 'ingredients'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    recipe = relationship(Recipe)
    amount = Column(Integer)
    unit = Column(String(80))

class Consumable(Base):
    __tablename__ = 'consumables'
    name = Column(String(80))
    id = Column(Integer, primary_key = True)
    amount = Column(Integer)
    unit = Column(String(80))

Base.metadata.create_all(engine)