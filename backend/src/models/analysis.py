from datetime import datetime
from src.extensions import db
import json

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    summary = db.Column(db.Text)
    plagiarism_score = db.Column(db.Float)
    critique_json = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    citations = db.relationship('Citation', backref='analysis', lazy=True, cascade='all, delete-orphan')
    
    @property
    def critique(self):
        """Get critique as Python dict."""
        if self.critique_json:
            try:
                return json.loads(self.critique_json)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @critique.setter
    def critique(self, value):
        """Set critique from Python dict."""
        if value:
            self.critique_json = json.dumps(value)
        else:
            self.critique_json = None
    
    def to_dict(self):
        """Convert analysis to dictionary."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'summary': self.summary,
            'plagiarism_score': self.plagiarism_score,
            'critique': self.critique,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'citations': [citation.to_dict() for citation in self.citations]
        }
    
    def __repr__(self):
        return f'<Analysis {self.id}>'