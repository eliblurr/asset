from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint, event
from mixins import BaseMixin
from config import settings
from database import Base

# class Audio():
    # pass

class Upload(BaseMixin, Base):
    '''Upload Model'''
    __tablename__ = "uploads"

    url = Column(String, nullable=False)

    # __table_args__ = (
    #     CheckConstraint(
    #         """
    #             (
    #                 (ad_id IS NOT NULL AND COALESCE(meal_id, menu_id, category_id, restaurant_id) IS NULL)
    #             OR  (meal_id IS NOT NULL AND COALESCE(ad_id, menu_id, category_id, restaurant_id) IS NULL) 
    #             OR  (menu_id IS NOT NULL AND COALESCE(meal_id, ad_id, category_id, restaurant_id) IS NULL) 
    #             OR  (category_id IS NOT NULL AND COALESCE(meal_id, menu_id, ad_id, restaurant_id) IS NULL) 
    #             OR  (restaurant_id IS NOT NULL AND COALESCE(meal_id, menu_id, category_id, ad_id) IS NULL) 
    #             ) 
    #             AND COALESCE(ad_id, meal_id, menu_id, category_id, restaurant_id) IS NOT NULL
    #         """
    #     , name="ck_img_assoc_single_fk_allowed"),
    # )

    
    # ad_id = Column(Integer, ForeignKey('ads.id'))
    # meal_id = Column(Integer, ForeignKey('meals.id'))
    # menu_id = Column(Integer, ForeignKey('menus.id'))
    # category_id = Column(Integer, ForeignKey('categories.id'))
    # restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    
@event.listens_for(Image, 'after_delete')
def remove_file(mapper, connection, target):
    # Remove from File System after_delete
    pass