from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from handlers.fsm.add_group import router as router_add_group
from handlers.fsm.add_faculty import router as router_add_faculty
from handlers.fsm.add_department import router as router_add_department
from handlers.fsm.edit_group import router as router_edit_group
from handlers.fsm.edit_department import router as router_edit_department
from handlers.fsm.edit_faculty import router as router_edit_faculty
from handlers.fsm.registration import router as router_registration

router = Router(name="fsm-commands")


@router.message(Command("cancel"))
@router.message(F.text == '-')
async def cancel_handler(msg: types.Message, state: FSMContext):
    if await state.get_state() is None:
        return
    await state.clear()
    await msg.answer('Дію було відмінено.')


router.include_router(router_add_faculty)
router.include_router(router_add_department)
router.include_router(router_add_group)
router.include_router(router_edit_faculty)
router.include_router(router_edit_department)
router.include_router(router_edit_group)
router.include_router(router_registration)
