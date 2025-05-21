from crud.base import CRUDBase
from domains.appraisal.models.appraisal import Appraisal
from domains.appraisal.schemas.appraisal import AppraisalCreate, AppraisalUpdate


class CRUDAppraisal(CRUDBase[Appraisal, AppraisalCreate, AppraisalUpdate]):
    pass


appraisal_actions = CRUDAppraisal(Appraisal)
