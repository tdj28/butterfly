# EXP-233 stops on primary-family `xtol`; EXP-234 is frozen

The first period-24 switch attempt stops before receipt because its inherited
primary-tangent helper rejects an optimizer status before residual inspection.
EXP-234 adopts the same explicit, residual-gated `xtol` handling validated by
EXP-232 and records every primary correction status. No switch or scientific
threshold changes.
