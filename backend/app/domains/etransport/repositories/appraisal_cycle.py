from crud.base import CRUDBase
from domains.appraisal.models.appraisal_cycle import AppraisalCycle
from domains.appraisal.schemas.appraisal_cycle import AppraisalCycleCreate, AppraisalCycleUpdate


class CRUDAppraisalCycle(CRUDBase[AppraisalCycle, AppraisalCycleCreate, AppraisalCycleUpdate]):
    pass


appraisal_cycle_actions = CRUDAppraisalCycle(AppraisalCycle)
