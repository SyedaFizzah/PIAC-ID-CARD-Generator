class InternCreate(BaseModel):
    name: str
    father_name: str
    gender: str
    university: str
    discipline: str
    department: str
    cnic: str
    skills: Optional[str] = None
    start_date: date
    end_date: date
    supervisor_id: Optional[int] = None
    manager_id: Optional[int] = None


class InternUpdate(BaseModel):
    name: Optional[str] = None
    father_name: Optional[str] = None
    gender: Optional[str] = None
    skills: Optional[str] = None
    university: Optional[str] = None
    discipline: Optional[str] = None
    department: Optional[str] = None
    cnic: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_description: Optional[str] = None
    supervisor_id: Optional[int] = None
    manager_id: Optional[int] = None


class InternOut(BaseModel):
    id: int
    unique_id: str
    name: str
    father_name: str
    gender: str
    university: str
    discipline: str
    department: str
    cnic: str
    skills: Optional[str] = None
    start_date: date
    duration_weeks: int
    valid_until: date
    photo_path: str
    ID_card_front_path: Optional[str] = None
    ID_card_back_path: Optional[str] = None
    university_id_card_front_path: Optional[str] = None
    university_id_card_back_path: Optional[str] = None
    cnic_front_path: Optional[str] = None
    cnic_back_path: Optional[str] = None
    CV_path: Optional[str] = None
    project_description: Optional[str] = None
    certificate_path: Optional[str] = None
    supervisor_id: Optional[int] = None
    manager_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InternVerifyOut(BaseModel):
    unique_id: str
    name: str
    department: Optional[str] = None
    valid_until: date
    status: str

    class Config:
        from_attributes = True