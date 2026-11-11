import subprocess, os
E = {
1: r"\frac{dN}{dt} = \alpha N",
2: r"\alpha = \alpha_0 N^{1/k}",
3: r"N = \frac{K}{\tau^{k}}, \qquad \tau = t_0 - t",
4: r"\alpha = \alpha_0 N^{1/k}\, f\!\left(N/N_\infty\right), \qquad f(0) = 1, \quad f(1) = 0",
5: r"\frac{dT}{dt} = g\, N^{\beta}\, T",
6: r"\mu(a) = \mu_{\mathrm{pre}}(a)^{\,1-m}\; \mu_{\mathrm{mod}}(a)^{\,m}, \qquad m = 1 - \left[1 + \frac{y-1}{y_M}\right]^{-a_M}",
7: r"F = F_\infty + \frac{F_0 - F_\infty}{1 + \left[(y-1)/y_F\right]^{b}}",
8: r"\frac{\partial n}{\partial t} + \frac{\partial n}{\partial a} = -\mu(a)\, n, \qquad n(0,t) = \tfrac{1}{2}\, F \int \varphi(a)\, n(a,t)\, da",
9: r"\frac{dT_j}{dt} = s_j\, g\, N_{\mathrm{world}}^{\,\beta}\, T_j",
10: r"Y = q\,L",
11: r"\frac{1}{q}\frac{dq}{dt} = (x_0 + \delta)\left(\frac{R}{R_0}\right)\left(\frac{q}{q_0}\right)^{-\lambda} - \delta",
}
for n,s in E.items():
    tex = r"""\documentclass[11pt,border=2pt]{standalone}
\usepackage{amsmath,amssymb}
\begin{document}
\begin{minipage}{15cm}
\begin{equation*}
%s \tag{%d}
\end{equation*}
\end{minipage}
\end{document}
""" % (s, n)
    open(f"eq{n}.tex","w").write(tex)
    r = subprocess.run(["pdflatex","-interaction=nonstopmode",f"eq{n}.tex"],capture_output=True,text=True)
    if r.returncode: print("FAIL",n, r.stdout[-800:])
    subprocess.run(["pdftoppm","-png","-r","300","-singlefile",f"eq{n}.pdf",f"eq{n}"])
print(sorted(f for f in os.listdir('.') if f.endswith('.png')))
