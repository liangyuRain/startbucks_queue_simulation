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
axis([0 40 0 0.2])
text(15+0.5,0.1+0.002,'$N=15,\lambda=0.1$','Interpreter','latex');
print('-f1','arrival_lambda','-depsc');

lambda=1.38;
x=1:5;
y=poisspdf(x-1,lambda-1)
figure(2)
plot(x,y); hold on
axis([1 5 0 1])
xticks([1 2 3 4 5])
xlabel('$k$','Interpreter','latex');
ylabel('$P(X=k)$','Interpreter','latex');
print('-f2','pois_dist','-depsc');

% population vs time
x=0:3600;
y=dlmread('total population vs time 1 hour.txt');
figure(3)
plot(x,y(1,:)); hold on
plot(x,y(2,:)); hold on
plot(x,y(3,:)); hold on
plot(x,y(4,:)); hold on
xlabel('Time Elapsed (s)');
ylabel('Number of Customer in Model');
axis([0 3600 0 53])
legend('One line without pickup','One line with pickup','Multiple lines without pickup','Multiple lines with pickup','location','best');
print('-f3','population_vs_time','-depsc');

% wait_time per item vs time
y=dlmread('wait time per item 1 hour.txt');
figure(4)
for i=0:3
    a=[];
    b=[];
    for j=1:length(y(i*2+1,:))
        if y(i*2+2,j) ~= 0
            a=[a y(i*2+2,j)];
            b=[b y(i*2+1,j)];
        end
    end
    plot(a,b); hold on
end
xlabel('Time Elapse (min)');
ylabel('Average Wait Time with One Item (s)');
legend('One line without pickup','One line with pickup','Multiple lines without pickup','Multiple lines with pickup','location','best');
print('-f4','wait_time_one_item','-depsc');

% people served vs window
x=1:10
y2=dlmread('people served vs window 10 second.txt');
figure(5);
plot(x,y2(1,1:10)); hold on
plot(x,y2(2,1:10)); hold on
xlabel('Number of Windows');
ylabel('Number of People Served in an Hour');
legend('One line with pickup','Multiple lines with pickup','location','best');
print('-f5','people_vs_window','-depsc');

% population vs time
x=0:360;
y=dlmread('queue length vs time ext.txt');
figure(6)
plot(x,y(1,1:361)); hold on
plot(x,y(2,1:361)); hold on
plot(x,y(3,1:361)); hold on
plot(x,y(4,1:361)); hold on
xlabel('Time Elapsed (s)');
ylabel('Order Placement Queue Length');
axis([0 360 0 60])
legend('One line without pickup','One line with pickup','Multiple lines without pickup','Multiple lines with pickup','location','best');
print('-f6','queue_length_vs_time_ext','-depsc');