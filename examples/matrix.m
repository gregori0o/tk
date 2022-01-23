A = eye(3);
B = ones(3);
C = A .+ B;
print C;

D = zeros(3, 4);
D[0, 0] = 42;
D[2:0, 2:4] -= 7;
D[1:3, 0:2] = 1;
print D;
D[1:3, 0:2] = D[1:3, 0:2] .* (D[1:3, 2:4] * 5) ;
print D;
print "";
D[0] += 100;
print -D;
print D[2, 2];
