"""
Modelli database usando SQLAlchemy
"""
from sqlalchemy import create_engine, Column, String, Boolean, Integer, Float, DateTime, Text, ForeignKey, JSON, Date, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """Modello utente"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(20), nullable=False)  # 'cliente' o 'negoziante'
    full_name = Column(String(255))
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    shops = relationship("Shop", back_populates="owner")
    customer_photos = relationship("CustomerPhoto", back_populates="user")
    outfits = relationship("Outfit", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")


class Shop(Base):
    """Modello negozio"""
    __tablename__ = "shops"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    owner = relationship("User", back_populates="shops")
    products = relationship("Product", back_populates="shop")
    customer_photos = relationship("CustomerPhoto", back_populates="shop")
    outfits = relationship("Outfit", back_populates="shop")
    purchases = relationship("Purchase", back_populates="shop")
    statistics = relationship("Statistic", back_populates="shop")
    prompts = relationship("Prompt", back_populates="shop")


class Product(Base):
    """Modello prodotto/capo"""
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # 'vestiti', 'scarpe', 'accessori'
    season = Column(String(20))  # 'primavera', 'estate', 'autunno', 'inverno', 'tutto'
    occasion = Column(String(50))  # 'casual', 'formale', 'sport', etc.
    style = Column(String(50))
    price = Column(Float)
    image_url = Column(Text)
    available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    shop = relationship("Shop", back_populates="products")
    outfit_products = relationship("OutfitProduct", back_populates="product")
    generated_images = relationship("GeneratedImage", back_populates="product")
    purchases = relationship("Purchase", back_populates="product")


class CustomerPhoto(Base):
    """Modello foto cliente"""
    __tablename__ = "customer_photos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"))
    image_url = Column(Text, nullable=False)
    angle = Column(String(50))  # 'frontale', 'laterale', 'posteriore'
    consent_given = Column(Boolean, default=False)
    uploaded_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relazioni
    user = relationship("User", back_populates="customer_photos")
    shop = relationship("Shop", back_populates="customer_photos")
    generated_images = relationship("GeneratedImage", back_populates="customer_photo")


class Outfit(Base):
    """Modello outfit"""
    __tablename__ = "outfits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relazioni
    user = relationship("User", back_populates="outfits")
    shop = relationship("Shop", back_populates="outfits")
    outfit_products = relationship("OutfitProduct", back_populates="outfit")
    generated_images = relationship("GeneratedImage", back_populates="outfit")
    purchases = relationship("Purchase", back_populates="outfit")


class OutfitProduct(Base):
    """Tabella di relazione many-to-many tra outfit e prodotti"""
    __tablename__ = "outfit_products"
    
    outfit_id = Column(UUID(as_uuid=True), ForeignKey("outfits.id"), primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True)
    
    # Relazioni
    outfit = relationship("Outfit", back_populates="outfit_products")
    product = relationship("Product", back_populates="outfit_products")


class GeneratedImage(Base):
    """Modello immagine generata dall'AI"""
    __tablename__ = "generated_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_photo_id = Column(UUID(as_uuid=True), ForeignKey("customer_photos.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    outfit_id = Column(UUID(as_uuid=True), ForeignKey("outfits.id"))
    image_url = Column(Text, nullable=False)
    prompt_used = Column(Text)
    scenario = Column(String(255))
    ai_service = Column(String(50))  # 'banana_pro', 'gemini'
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relazioni
    customer_photo = relationship("CustomerPhoto", back_populates="generated_images")
    product = relationship("Product", back_populates="generated_images")
    outfit = relationship("Outfit", back_populates="generated_images")


class Purchase(Base):
    """Modello acquisto"""
    __tablename__ = "purchases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    outfit_id = Column(UUID(as_uuid=True), ForeignKey("outfits.id"))
    purchase_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    amount = Column(Float)
    status = Column(String(20), default='completed')
    
    # Relazioni
    user = relationship("User", back_populates="purchases")
    shop = relationship("Shop", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")
    outfit = relationship("Outfit", back_populates="purchases")


class Statistic(Base):
    """Modello statistica"""
    __tablename__ = "statistics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float)
    date = Column(Date, default=datetime.utcnow)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relazioni
    shop = relationship("Shop", back_populates="statistics")


class Prompt(Base):
    """Modello prompt predefinito"""
    __tablename__ = "prompts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"))
    category = Column(String(50))
    base_prompt = Column(Text, nullable=False)
    variables = Column(JSON)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    shop = relationship("Shop", back_populates="prompts")




