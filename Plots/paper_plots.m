clear all; close all; clc

lambda0=0.2;
k=log(2)/15;
x=linspace(0,40);
y=lambda0*exp(-k*x);

figure(1)
plot(x,y); hold on
xlabel('$N$','Interpreter','latex');
ylabel('$\lambda\ \ \ $','Interpreter','latex','Rotation',0);
plot(15,0.1,'*'); hold on
text(15+0.5,0.1+0.002,'$N=15,\lambda=0.1$','Interpreter','latex');
print('-f1','arrival_lambda','-depsc');