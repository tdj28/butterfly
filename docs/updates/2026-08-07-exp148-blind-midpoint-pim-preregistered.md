# Update — EXP-148 blind midpoint PIM preregistered

EXP-147 passes all 198 midpoint lobe traces and retains 989/558 fine/coarse
left-lobe points. That reference was completed without any midpoint PIM data.

EXP-148 now freezes the independent saddle reconstruction at `a=0.1481875`
under the unchanged EXP-128 method. Its expected branch count is null. Once the
long-running EXP-132 releases the local workers, EXP-148 will determine the
blind two/three class; only afterward will a separate hash-bound EXP-149 test
whether left-lobe membership agrees prospectively.
